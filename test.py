#!/usr/bin/env python
# Automated script to run the pspautotests test suite in PPSSPP.

import sys
import os
import subprocess
import threading
import glob
import json


PPSSPP_EXECUTABLES = [
  # Windows
  "Windows\\Debug\\PPSSPPHeadless.exe",
  "Windows\\Release\\PPSSPPHeadless.exe",
  "Windows\\x64\\Debug\\PPSSPPHeadless.exe",
  "Windows\\x64\\Release\\PPSSPPHeadless.exe",
  "build*/PPSSPPHeadless.exe",
  "./PPSSPPHeadless.exe",
  # Mac
  "build*/Debug/PPSSPPHeadless",
  "build*/Release/PPSSPPHeadless",
  "build*/RelWithDebInfo/PPSSPPHeadless",
  "build*/MinSizeRel/PPSSPPHeadless",
  # Linux
  "build*/PPSSPPHeadless",
  "./PPSSPPHeadless",
  # CI
  "ppsspp/PPSSPPHeadless",
  "ppsspp\\PPSSPPHeadless.exe",
]

PPSSPP_EXE = None
TEST_ROOT = "pspautotests/tests/"
TIMEOUT = 5
BENCH_CONFIG_DEFAULT = "Tools/perf/benchmarks.json"

class Command(object):
  def __init__(self, cmd, data = None):
    self.cmd = cmd
    self.data = data
    self.process = None
    self.output = None
    self.timeout = False

  def run(self, timeout):
    def target():
      self.process = subprocess.Popen(self.cmd, stdin=subprocess.PIPE, stdout=sys.stdout, stderr=subprocess.STDOUT)
      self.process.stdin.write(self.data.encode('utf-8'))
      self.process.stdin.close()
      self.process.communicate()

    thread = threading.Thread(target=target)
    thread.start()

    thread.join(timeout)
    if thread.is_alive():
      self.timeout = True
      if sys.version_info < (2, 6):
        os.kill(self.process.pid, signal.SIGKILL)
      else:
        self.process.terminate()
      thread.join()

    return self.process.returncode

# Test names are the C files without the .c extension.
# These have worked and should keep working always - regression tests.
tests_good = [
  "cpu/cpu_alu/cpu_alu",
  "cpu/cpu_alu/cpu_branch",
  "cpu/cpu_alu/cpu_branch2",
  "cpu/vfpu/colors",
  "cpu/vfpu/convert",
  "cpu/vfpu/gum",
  "cpu/vfpu/matrix",
  "cpu/vfpu/vavg",
  "cpu/icache/icache",
  "cpu/lsu/lsu",
  "cpu/fpu/fpu",

  "audio/atrac/addstreamdata",
  "audio/atrac/atractest",
  "audio/atrac/decode",
  "audio/atrac/getremainframe",
  "audio/atrac/getsoundsample",
  "audio/atrac/ids",
  "audio/atrac/resetpos",
  "audio/atrac/resetting",
  "audio/atrac/replay",
  "audio/atrac/stream",
  "audio/atrac/reset2",
  "audio/atrac/second/resetting",
  "audio/atrac/second/getinfo",
  "audio/atrac/second/needed",
  "audio/atrac/second/setbuffer",
  "audio/atrac/setdata",
  "audio/atrac/sas",
  "audio/mp3/checkneeded",
  "audio/mp3/getbitrate",
  "audio/mp3/getchannel",
  "audio/mp3/getframenum",
  "audio/mp3/getloopnum",
  "audio/mp3/getmaxoutput",
  "audio/mp3/getmpegversion",
  "audio/mp3/getsamplerate",
  "audio/mp3/getsumdecoded",
  "audio/mp3/initresource",
  "audio/mp3/mp3test",
  "audio/mp3/release",
  "audio/mp3/reserve",
  "audio/mp3/setloopnum",
  "audio/output2/changelength",
  "audio/output2/reserve",
  "audio/output2/threads",
  "audio/reverb/basic",
  "audio/reverb/volume",
  "audio/sascore/sascore",
  "audio/sascore/adsrcurve",
  "audio/sascore/getheight",
  "audio/sascore/keyoff",
  "audio/sascore/keyon",
  "audio/sascore/noise",
  "audio/sascore/outputmode",
  "audio/sascore/pause",
  "audio/sascore/pcm",
  "audio/sascore/pitch",
  "audio/sascore/vag",
  "ctrl/ctrl",
  "ctrl/idle/idle",
  "ctrl/sampling/sampling",
  "ctrl/sampling2/sampling2",
  "ctrl/vblank",
  "display/display",
  "display/vblankmulti",
  "display/isstate",
  "display/setframebuf",
  "display/setmode",
  "dmac/dmactest",
  "font/altcharcode",
  "font/charimagerect",
  "font/find",
  "font/fontinfo",
  "font/fontinfobyindex",
  "font/fontlist",
  "font/optimum",
  "font/resolution",
  "font/shadowimagerect",
  "gpu/bounding/count",
  "gpu/bounding/planes",
  "gpu/bounding/vertexaddr",
  "gpu/bounding/viewport",
  "gpu/callbacks/ge_callbacks",
  "gpu/clipping/homogeneous",
  "gpu/clut/address",
  "gpu/clut/masks",
  "gpu/clut/offset",
  "gpu/clut/shifts",
  "gpu/commands/basic",
  "gpu/commands/blend",
  "gpu/commands/blend565",
  "gpu/commands/blocktransfer",
  "gpu/commands/cull",
  "gpu/commands/fog",
  "gpu/commands/material",
  "gpu/complex/complex",
  "gpu/displaylist/alignment",
  "gpu/dither/dither",
  "gpu/filtering/mipmaplinear",
  "gpu/ge/break",
  "gpu/ge/context",
  "gpu/ge/edram",
  "gpu/ge/enqueueparam",
  "gpu/ge/queue",
  "gpu/primitives/indices",
  "gpu/primitives/invalidprim",
  "gpu/primitives/points",
  "gpu/primitives/rectangles",
  "gpu/primitives/trianglefan",
  "gpu/primitives/trianglestrip",
  "gpu/primitives/triangles",
  "gpu/rendertarget/copy",
  "gpu/rendertarget/depal",
  "gpu/signals/pause",
  "gpu/signals/pause2",
  "gpu/signals/suspend",
  "gpu/signals/sync",
  "gpu/texcolors/dxt1",
  "gpu/texcolors/dxt3",
  "gpu/texcolors/dxt5",
  "gpu/texcolors/rgb565",
  "gpu/texcolors/rgba4444",
  "gpu/texcolors/rgba5551",
  "gpu/texfunc/add",
  "gpu/texfunc/blend",
  "gpu/texfunc/decal",
  "gpu/texfunc/modulate",
  "gpu/texfunc/replace",
  "gpu/textures/mipmap",
  "gpu/textures/rotate",
  "gpu/transfer/invalid",
  "gpu/transfer/mirrors",
  "gpu/transfer/overlap",
  "gpu/vertices/colors",
  "gpu/vertices/morph",
  # "gpu/vertices/texcoords",  #  See issue #19093
  "hash/hash",
  "hle/check_not_used_uids",
  "intr/intr",
  "intr/enablesub",
  "intr/suspended",
  "intr/vblank/vblank",
  "io/cwd/cwd",
  "io/open/badparent",
  "jpeg/create",
  "jpeg/delete",
  "jpeg/finish",
  "jpeg/init",
  "loader/bss/bss",
  "malloc/malloc",
  "misc/dcache",
  "misc/deadbeef",
  "misc/libc",
  "misc/sdkver",
  "misc/testgp",
  "misc/timeconv",
  "misc/reg",
  "mstick/mstick",
  "power/cpu",
  "power/power",
  "power/volatile/lock",
  "power/volatile/trylock",
  "power/volatile/unlock",
  "rtc/rtc",
  "rtc/arithmetic",
  "rtc/lookup",
  "string/string",
  "sysmem/freesize",
  "sysmem/memblock",
  "sysmem/sysmem",
  "sysmem/volatile",
  "threads/alarm/alarm",
  "threads/alarm/cancel/cancel",
  "threads/alarm/refer/refer",
  "threads/alarm/set/set",
  "threads/callbacks/callbacks",
  "threads/callbacks/check",
  "threads/callbacks/create",
  "threads/callbacks/delete",
  "threads/callbacks/exit",
  "threads/callbacks/refer",
  "threads/events/events",
  "threads/events/cancel/cancel",
  "threads/events/clear/clear",
  "threads/events/create/create",
  "threads/events/delete/delete",
  "threads/events/poll/poll",
  "threads/events/refer/refer",
  "threads/events/set/set",
  "threads/events/wait/wait",
  "threads/fpl/fpl",
  "threads/fpl/allocate",
  "threads/fpl/cancel",
  "threads/fpl/create",
  "threads/fpl/delete",
  "threads/fpl/free",
  "threads/fpl/priority",
  "threads/fpl/refer",
  "threads/fpl/tryallocate",
  "threads/k0/k0",
  "threads/lwmutex/create",
  "threads/lwmutex/delete",
  "threads/lwmutex/lock",
  "threads/lwmutex/priority",
  "threads/lwmutex/refer",
  "threads/lwmutex/try",
  "threads/lwmutex/try600",
  "threads/lwmutex/unlock",
  "threads/mbx/mbx",
  "threads/mbx/cancel/cancel",
  "threads/mbx/create/create",
  "threads/mbx/delete/delete",
  "threads/mbx/poll/poll",
  "threads/mbx/priority/priority",
  "threads/mbx/receive/receive",
  "threads/mbx/refer/refer",
  "threads/mbx/send/send",
  "threads/msgpipe/msgpipe",
  "threads/msgpipe/cancel",
  "threads/msgpipe/create",
  "threads/msgpipe/data",
  "threads/msgpipe/delete",
  "threads/msgpipe/receive",
  "threads/msgpipe/refer",
  "threads/msgpipe/send",
  "threads/msgpipe/tryreceive",
  "threads/msgpipe/trysend",
  "threads/mutex/cancel",
  "threads/mutex/create",
  "threads/mutex/delete",
  "threads/mutex/lock",
  "threads/mutex/mutex",
  "threads/mutex/priority",
  "threads/mutex/refer",
  "threads/mutex/try",
  "threads/mutex/unlock",
  "threads/mutex/unlock2",
  "threads/semaphores/semaphores",
  "threads/semaphores/cancel",
  "threads/semaphores/create",
  "threads/semaphores/delete",
  "threads/semaphores/fifo",
  "threads/semaphores/poll",
  "threads/semaphores/priority",
  "threads/semaphores/refer",
  "threads/semaphores/signal",
  "threads/semaphores/wait",
  "threads/threads/change",
  "threads/threads/exitstatus",
  "threads/threads/extend",
  "threads/threads/refer",
  "threads/threads/release",
  "threads/threads/rotate",
  "threads/threads/stackfree",
  "threads/threads/start",
  "threads/threads/suspend",
  "threads/threads/threadend",
  "threads/threads/threadmanidlist",
  "threads/threads/threadmanidtype",
  "threads/threads/threads",
  "threads/tls/create",
  "threads/tls/delete",
  "threads/tls/free",
  "threads/tls/priority",
  "threads/tls/refer",
  "threads/vpl/allocate",
  "threads/vpl/cancel",
  "threads/vpl/delete",
  "threads/vpl/fifo",
  "threads/vpl/free",
  "threads/vpl/order",
  "threads/vpl/priority",
  "threads/vpl/refer",
  "threads/vpl/try",
  "threads/vpl/vpl",
  "threads/vtimers/vtimer",
  "threads/vtimers/cancelhandler",
  "threads/vtimers/create",
  "threads/vtimers/delete",
  "threads/vtimers/getbase",
  "threads/vtimers/gettime",
  "threads/vtimers/interrupt",
  "threads/vtimers/refer",
  "threads/vtimers/sethandler",
  "threads/vtimers/settime",
  "threads/vtimers/start",
  "threads/vtimers/stop",
  "threads/wakeup/wakeup",
  "utility/msgdialog/abort",
  "utility/savedata/autosave",
  "utility/savedata/filelist",
  "utility/savedata/makedata",
  "umd/callbacks/umd",
  "umd/register",
  "video/mpeg/ringbuffer/avail",
  "video/mpeg/ringbuffer/construct",
  "video/mpeg/ringbuffer/destruct",
  "video/mpeg/ringbuffer/memsize",
  "video/mpeg/ringbuffer/packnum",
  "video/psmfplayer/break",
  "video/psmfplayer/create",
  "video/psmfplayer/delete",
  "video/psmfplayer/getaudiodata",
  "video/psmfplayer/getaudiooutsize",
  "video/psmfplayer/getcurrentpts",
  "video/psmfplayer/getcurrentstatus",
  "video/psmfplayer/getcurrentstream",
  "video/psmfplayer/getpsmfinfo",
  "video/psmfplayer/releasepsmf",
  "video/psmfplayer/selectspecific",
  "video/psmfplayer/setpsmf",
  "video/psmfplayer/settempbuf",
  "video/psmfplayer/stop",
]

tests_next = [
# These are the next tests up for fixing. These run by default.
  "cpu/fpu/fcr",
  "cpu/vfpu/prefixes",
  "cpu/vfpu/vector",
  "cpu/vfpu/vregs",
  "audio/sceaudio/datalen",
  "audio/sceaudio/output",
  "audio/sceaudio/reserve",
  "audio/sascore/setadsr",
  "audio/mp3/infotoadd",
  "audio/mp3/init",
  "audio/mp3/notifyadd",
  "audio/output2/frequency",
  "audio/output2/release",
  "audio/output2/rest",
  "ccc/convertstring",
  "display/hcount",
  "font/fonttest",
  "font/charglyphimage",
  "font/charglyphimageclip",
  "font/charinfo",
  "font/newlib",
  "font/open",
  "font/openfile",
  "font/openmem",
  "font/shadowglyphimage",
  "font/shadowglyphimageclip",
  "font/shadowinfo",
  "gpu/clipping/guardband",
  "gpu/commands/light",
  "gpu/depth/precision",
  "gpu/displaylist/state",
  "gpu/filtering/linear",
  "gpu/filtering/nearest",
  "gpu/filtering/precisionlinear2d",
  "gpu/filtering/precisionlinear3d",
  "gpu/filtering/precisionnearest2d",
  "gpu/filtering/precisionnearest3d",
  "gpu/ge/edramswizzle",
  "gpu/ge/get",
  "gpu/primitives/bezier",
  "gpu/primitives/continue",
  "gpu/primitives/immediate",
  "gpu/primitives/lines",
  "gpu/primitives/linestrip",
  "gpu/primitives/spline",
  "gpu/reflection/reflection",
  "gpu/rendertarget/rendertarget",
  "gpu/signals/continue",
  "gpu/signals/jumps",
  "gpu/signals/simple",
  "gpu/simple/simple",
  "gpu/texmtx/normals",
  "gpu/texmtx/prims",
  "gpu/texmtx/source",
  "gpu/texmtx/uvs",
  "gpu/textures/size",
  "gpu/triangle/triangle",
  "intr/registersub",
  "intr/releasesub",
  "intr/waits",
  "io/directory/directory",
  "io/file/file",
  "io/file/rename",
  "io/io/io",
  "io/iodrv/iodrv",
  "io/open/tty0",
  "jpeg/csc",
  "jpeg/decode",
  "jpeg/decodes",
  "jpeg/decodeycbcr",
  "jpeg/decodeycbcrs",
  "jpeg/getoutputinfo",
  "jpeg/mjpegcsc",
  # Doesn't work on a PSP for security reasons, hangs in PPSSPP currently.
  # Commented out to make tests run much faster.
  #"modules/loadexec/loader",
  "net/http/http",
  "net/primary/ether",
  "power/freq",
  "rtc/convert",
  "sysmem/partition",
  "threads/callbacks/cancel",
  "threads/callbacks/count",
  "threads/callbacks/notify",
  "threads/scheduling/dispatch",
  "threads/scheduling/scheduling",
  "threads/threads/create",
  "threads/threads/terminate",
  "threads/tls/get",
  "threads/vpl/create",
  "umd/io/umd_io",
  "umd/raw_access/raw_access",
  "umd/wait/wait",
  "utility/msgdialog/dialog",
  "utility/savedata/getsize",
  "utility/savedata/idlist",
  # These tests appear to be broken and just hang.
  #"utility/savedata/deletebroken",
  #"utility/savedata/deletedata",
  #"utility/savedata/deleteemptyfilename",
  #"utility/savedata/loadbroken",
  #"utility/savedata/loaddata",
  #"utility/savedata/loademptyfilename",
  #"utility/savedata/saveemptyfilename",
  "utility/savedata/secureversion",
  "utility/savedata/sizes",
  "utility/systemparam/systemparam",
  "video/mpeg/basic",
  "video/pmf/pmf",
  "video/pmf_simple/pmf_simple",
  "video/psmfplayer/basic",
  "video/psmfplayer/configplayer",
  "video/psmfplayer/getvideodata",
  "video/psmfplayer/playmode",
  "video/psmfplayer/selectstream",
  "video/psmfplayer/setpsmfoffset",
  "video/psmfplayer/start",
  "video/psmfplayer/update",
]


# These are the tests we ignore (not important, or impossible to run)
tests_ignored = [
  "kirk/kirk",
  "me/me",
]



def init():
  global PPSSPP_EXE, TEST_ROOT
  if not os.path.exists("pspautotests"):
    if os.path.exists(os.path.dirname(__file__) + "/pspautotests"):
      TEST_ROOT = os.path.dirname(__file__) + "/pspautotests/tests/";
    else:
      print("Please run git submodule init; git submodule update;")
      sys.exit(1)

  if not os.path.exists(TEST_ROOT + "cpu/cpu_alu/cpu_alu.prx"):
    print("Please install the pspsdk and run make in common/ and in all the tests")
    print("(checked for existence of cpu/cpu_alu/cpu_alu.prx)")
    sys.exit(1)

  possible_exes = [glob.glob(f) for f in PPSSPP_EXECUTABLES]
  possible_exes = [x for sublist in possible_exes for x in sublist]
  existing = filter(os.path.exists, possible_exes)
  if existing:
    PPSSPP_EXE = max((os.path.getmtime(f), f) for f in existing)[1]
  else:
    PPSSPP_EXE = None

  if not PPSSPP_EXE:
    print("PPSSPPHeadless executable missing, please build one.")
    sys.exit(1)

def run_tests(test_list, args):
  global PPSSPP_EXE, TIMEOUT
  returncode = 0
  test_filenames = []

  for test in test_list:
    # Try prx first
    elf_filename = TEST_ROOT + test + ".prx"
    if not os.path.exists(elf_filename):
      print("WARNING: no prx, trying elf")
      elf_filename = TEST_ROOT + test + ".elf"

    test_filenames.append(elf_filename)

  if len(test_filenames):
    # TODO: Maybe --compare should detect --graphics?
    cmdline = [PPSSPP_EXE, '--root', TEST_ROOT + '../', '--compare', '--timeout=' + str(TIMEOUT), '@-']
    cmdline.extend([i for i in args if i not in ['-g', '-m', '-b']])

    c = Command(cmdline, '\n'.join(test_filenames))
    returncode = c.run(TIMEOUT * len(test_filenames))

    print("Ran " + ' '.join(cmdline))

  return returncode

def load_bench_config(config_path):
  if not os.path.exists(config_path):
    print("Benchmark config not found: " + config_path)
    sys.exit(1)

  with open(config_path, "r") as f:
    config = json.load(f)

  tests = []
  for entry in config.get("tests", []):
    if isinstance(entry, dict):
      if "test" in entry:
        tests.append(entry["test"])
    elif isinstance(entry, str):
      tests.append(entry)

  return {
    "tests": tests,
    "default_bench_runs": config.get("default_bench_runs"),
    "default_repetitions": config.get("default_repetitions"),
  }

def parse_bench_record(line, prefix):
  if not line.startswith(prefix):
    return None
  payload = line[len(prefix):].strip()
  if not payload:
    return None
  try:
    return json.loads(payload)
  except ValueError:
    return None

def parse_requested_gpu_backend(headless_args):
  for arg in headless_args:
    if arg.startswith("--graphics="):
      return arg[len("--graphics="):]
    if arg == "--graphics":
      return "default"
  return "default"

def run_benchmarks(test_list, args, bench_runs, bench_repetitions, bench_output):
  global PPSSPP_EXE, TIMEOUT
  returncode = 0
  bench_results = []
  bench_meta_records = []
  headless_args = [i for i in args if i not in ['-g', '-m', '-b']]
  requested_gpu_backend = parse_requested_gpu_backend(headless_args)

  for test in test_list:
    # Try prx first
    test_filename = TEST_ROOT + test + ".prx"
    if not os.path.exists(test_filename):
      print("WARNING: no prx, trying elf")
      test_filename = TEST_ROOT + test + ".elf"

    for repetition in range(bench_repetitions):
      cmdline = [
        PPSSPP_EXE,
        '--root',
        TEST_ROOT + '../',
        '--bench',
        '--bench-runs=' + str(bench_runs),
        '--timeout=' + str(TIMEOUT),
        test_filename,
      ]
      cmdline.extend(headless_args)

      process = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
      output, _ = process.communicate()
      if output:
        sys.stdout.write(output)

      bench_meta = None
      bench_result = None
      if output:
        for line in output.splitlines():
          meta = parse_bench_record(line, "BENCH_META ")
          if meta is not None:
            bench_meta = meta
          parsed = parse_bench_record(line, "BENCH_RESULT ")
          if parsed is not None:
            bench_result = parsed

      if bench_result is None:
        print("ERROR: Missing BENCH_RESULT output for " + test)
        returncode = process.returncode if process.returncode else 1
      else:
        bench_result["requested_test"] = test
        bench_result["repetition"] = repetition + 1
        bench_result["requested_gpu_backend"] = requested_gpu_backend
        bench_results.append(bench_result)
        if bench_meta is not None:
          bench_meta["requested_test"] = test
          bench_meta["repetition"] = repetition + 1
          bench_meta["requested_gpu_backend"] = requested_gpu_backend
          bench_meta_records.append(bench_meta)

      if process.returncode != 0 and returncode == 0:
        returncode = process.returncode

      print("Ran " + ' '.join(cmdline))

  if bench_results:
    grouped = {}
    for result in bench_results:
      test_id = result.get("test_id", result.get("requested_test", "unknown"))
      grouped.setdefault(test_id, []).append(result)

    print("Benchmark summary:")
    for test_id in sorted(grouped):
      samples = grouped[test_id]
      avg_seconds = sum(float(sample.get("avg_seconds", 0.0)) for sample in samples) / float(len(samples))
      avg_rps = sum(float(sample.get("runs_per_second", 0.0)) for sample in samples) / float(len(samples))
      print("  {} - avg_seconds={:.6f}, runs_per_second={:.3f}, samples={}".format(test_id, avg_seconds, avg_rps, len(samples)))

  if bench_output:
    payload = {
      "schema": "ppsspp_testpy_bench_v1",
      "bench_runs": bench_runs,
      "bench_repetitions": bench_repetitions,
      "meta": bench_meta_records,
      "results": bench_results,
    }
    output_dir = os.path.dirname(bench_output)
    if output_dir and not os.path.exists(output_dir):
      os.makedirs(output_dir)
    with open(bench_output, "w") as f:
      json.dump(payload, f, indent=2, sort_keys=True)
    print("Wrote benchmark report to " + bench_output)

  return returncode

def main():
  init()
  tests = []
  args = []
  teamcity = False
  bench_mode = False
  bench_config = BENCH_CONFIG_DEFAULT
  bench_output = None
  bench_runs = None
  bench_repetitions = None

  for arg in sys.argv[1:]:
    if arg == '--teamcity':
      args.append(arg)
      teamcity = True
    elif arg == '--bench':
      bench_mode = True
    elif arg.startswith('--bench-config='):
      bench_config = arg[len('--bench-config='):]
    elif arg.startswith('--bench-output='):
      bench_output = arg[len('--bench-output='):]
    elif arg.startswith('--bench-runs='):
      bench_runs = max(1, int(arg[len('--bench-runs='):]))
    elif arg.startswith('--bench-repetitions='):
      bench_repetitions = max(1, int(arg[len('--bench-repetitions='):]))
    elif arg[0] == '-':
      args.append(arg)
    else:
      tests.append(arg)

  if not tests:
    if bench_mode and '-g' not in args and '-b' not in args:
      tests = []
    elif '-g' in args:
      tests = tests_good
    elif '-b' in args:
      tests = tests_next
    else:
      tests = tests_next + tests_good
  elif '-m' in args and '-g' in args:
    tests = [i for i in tests_good if i.startswith(tests[0])]
  elif '-m' in args and '-b' in args:
    tests = [i for i in tests_next if i.startswith(tests[0])]
  elif '-m' in args:
    tests = [i for i in tests_next + tests_good if i.startswith(tests[0])]

  if bench_mode:
    if not tests:
      config = load_bench_config(bench_config)
      tests = config["tests"]
      if bench_runs is None and config["default_bench_runs"] is not None:
        bench_runs = max(1, int(config["default_bench_runs"]))
      if bench_repetitions is None and config["default_repetitions"] is not None:
        bench_repetitions = max(1, int(config["default_repetitions"]))

    if not tests:
      print("No benchmark tests selected.")
      return 1

    if bench_runs is None:
      bench_runs = 100
    if bench_repetitions is None:
      bench_repetitions = 1
    returncode = run_benchmarks(tests, args, bench_runs, bench_repetitions, bench_output)
  else:
    returncode = run_tests(tests, args)

  if teamcity:
    return 0
  return returncode

exit(main())
