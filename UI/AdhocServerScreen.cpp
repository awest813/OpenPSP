#include "AdhocServerScreen.h"

#include "Common/Data/Text/I18n.h"
#include "Common/Net/Resolve.h"
#include "Common/StringUtils.h"
#include "Common/System/OSD.h"
#include "Common/System/System.h"
#include "Common/UI/PopupScreens.h"
#include "Common/UI/Root.h"

AdhocServerScreen::AdhocServerScreen(std::string *value, std::string_view title)
	: UI::PopupScreen(title, T(I18NCat::DIALOG, "OK"), T(I18NCat::DIALOG, "Cancel")), value_(value) {
	resolver_ = std::thread([](AdhocServerScreen *thiz) {
		thiz->ResolverThread();
	}, this);
	editValue_ = *value;

	auto list_to_use = defaultProAdhocServerList;
	downloadedProAdhocServerListMutex.lock();
	if (downloadedProAdhocServerList.size() != 0) {
		list_to_use = downloadedProAdhocServerList;
	}
	downloadedProAdhocServerListMutex.unlock();

	listItems_ = list_to_use;
}

AdhocServerScreen::~AdhocServerScreen() {
	{
		std::unique_lock<std::mutex> guard(resolverLock_);
		resolverState_ = ResolverState::QUIT;
		resolverCond_.notify_one();
	}
	resolver_.join();
}

void AdhocServerScreen::CreatePopupContents(UI::ViewGroup *parent) {
	using namespace UI;
	auto sy = GetI18NCategory(I18NCat::SYSTEM);
	auto di = GetI18NCategory(I18NCat::DIALOG);
	auto n = GetI18NCategory(I18NCat::NETWORKING);

	hostnameChoice_ = parent->Add(new PopupTextInputChoice(GetRequesterToken(), &editValue_, n->T("Hostname"), "", 256, screenManager()));

	parent->Add(new TextView(n->T("Ad hoc server list hint"), ALIGN_LEFT, true,
		new LinearLayoutParams(FILL_PARENT, WRAP_CONTENT, Margins(0, 4, 0, 0))));

	struct PickRow {
		std::string tagHost;
		std::string buttonText;
	};
	std::vector<PickRow> rows;
	for (const auto &item : listItems_) {
		if (item.hostname.empty()) {
			continue;
		}
		PickRow row;
		row.tagHost = item.hostname;
		if (!item.name.empty() && item.name != item.hostname) {
			row.buttonText = item.name + "\n" + item.hostname;
			if (!item.location.empty()) {
				row.buttonText += " — ";
				row.buttonText += item.location;
			}
		} else {
			row.buttonText = item.hostname;
		}
		rows.push_back(std::move(row));
	}
	{
		PickRow row;
		row.tagHost = "localhost";
		row.buttonText = "localhost";
		rows.push_back(std::move(row));
	}
	std::vector<std::string> listIP;
	net::GetLocalIP4List(listIP);
	for (const auto &label : listIP) {
		if (label.find("127.") != 0 && label.find("169.254.") != 0 && label.find("0.") != 0) {
			PickRow row;
			row.tagHost = label;
			row.buttonText = label;
			rows.push_back(std::move(row));
		}
	}

	parent->Add(new Spacer(5.0f));

	ScrollView *scrollView = new ScrollView(ORIENT_VERTICAL, new LinearLayoutParams(1.0f));
	LinearLayout *innerView = new LinearLayout(ORIENT_VERTICAL, new LinearLayoutParams(FILL_PARENT, WRAP_CONTENT));
	innerView->SetSpacing(5.0f);
	for (const auto &row : rows) {
		auto *rowLayout = innerView->Add(new LinearLayout(ORIENT_HORIZONTAL, new LinearLayoutParams(FILL_PARENT, WRAP_CONTENT)));
		rowLayout->SetSpacing(6.0f);
		Button *useBtn = rowLayout->Add(new Button(row.buttonText, new LinearLayoutParams(1.0f)));
		useBtn->SetTag(row.tagHost);
		useBtn->OnClick.Add([this](UI::EventParams &e) {
			std::string value = e.v->Tag();
			if (value.empty()) {
				return;
			}
			editValue_ = value;
			if (hostnameChoice_) {
				UI::EventParams ch{};
				ch.v = hostnameChoice_;
				hostnameChoice_->OnChange.Trigger(ch);
			}
			if (progressView_) {
				progressView_->SetVisibility(UI::V_GONE);
			}
		});
		Button *copyBtn = rowLayout->Add(new Button(di->T("Copy to clipboard"), new LinearLayoutParams(WRAP_CONTENT, WRAP_CONTENT)));
		copyBtn->SetTag(row.tagHost);
		copyBtn->OnClick.Add([di](UI::EventParams &e) {
			std::string value = e.v->Tag();
			if (!value.empty()) {
				System_CopyStringToClipboard(value);
				g_OSD.Show(OSDType::MESSAGE_INFO, ApplySafeSubstitutions(di->T("Copied to clipboard: %1"), value), 0.0f, "copyToClip");
			}
		});
	}

	scrollView->Add(innerView);
	parent->Add(scrollView);

	progressView_ = parent->Add(new NoticeView(NoticeLevel::INFO, n->T("Validating address..."), "", new LinearLayoutParams(Margins(0, 5, 0, 0))));
	progressView_->SetVisibility(UI::V_GONE);
}

void AdhocServerScreen::ResolverThread() {
	std::unique_lock<std::mutex> guard(resolverLock_);

	while (resolverState_ != ResolverState::QUIT) {
		resolverCond_.wait(guard);

		if (resolverState_ == ResolverState::QUEUED) {
			resolverState_ = ResolverState::PROGRESS;

			addrinfo *resolved = nullptr;
			std::string err;
			toResolveResult_ = net::DNSResolve(toResolve_, "80", &resolved, err);
			if (resolved)
				net::DNSResolveFree(resolved);

			resolverState_ = ResolverState::READY;
		}
	}
}

bool AdhocServerScreen::CanComplete(DialogResult result) {
	auto n = GetI18NCategory(I18NCat::NETWORKING);

	if (result != DR_OK)
		return true;

	std::string value = editValue_;
	if (lastResolved_ == value) {
		return true;
	}

	// Currently running.
	if (resolverState_ == ResolverState::PROGRESS)
		return false;

	std::lock_guard<std::mutex> guard(resolverLock_);
	switch (resolverState_) {
	case ResolverState::PROGRESS:
	case ResolverState::QUIT:
		return false;

	case ResolverState::QUEUED:
	case ResolverState::WAITING:
		break;

	case ResolverState::READY:
		if (toResolve_ == value) {
			// Reset the state, nothing there now.
			resolverState_ = ResolverState::WAITING;
			toResolve_.clear();
			lastResolved_ = value;
			lastResolvedResult_ = toResolveResult_;

			if (lastResolvedResult_) {
				progressView_->SetVisibility(UI::V_GONE);
			} else {
				progressView_->SetText(n->T("Invalid IP or hostname"));
				progressView_->SetLevel(NoticeLevel::ERROR);
				progressView_->SetVisibility(UI::V_VISIBLE);
			}
			return true;
		}

		// Throw away that last result, it was for a different value.
		break;
	}

	resolverState_ = ResolverState::QUEUED;
	toResolve_ = value;
	resolverCond_.notify_one();

	progressView_->SetText(n->T("Validating address..."));
	progressView_->SetLevel(NoticeLevel::INFO);
	progressView_->SetVisibility(UI::V_VISIBLE);

	return false;
}

void AdhocServerScreen::OnCompleted(DialogResult result) {
	if (result == DR_OK) {
		*value_ = StripSpaces(editValue_);
	}
}
