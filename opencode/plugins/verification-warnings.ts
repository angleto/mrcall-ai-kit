import type { Plugin } from "@opencode-ai/plugin"
import { spawnSync } from "node:child_process"
import { join } from "node:path"
import { homedir } from "node:os"

export const VerificationWarnings: Plugin = async ({ client, directory }) => ({
  "tool.execute.before": async (input, _output) => {
    try {
      if (!input.sessionID || !directory) return
      const backend = join(homedir(), ".config/mrcall-ai-kit/verification-warnings/verification_warnings.py")
      const bridge = "import importlib.util,sys; s=importlib.util.spec_from_file_location('warnings_backend',sys.argv[1]); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); w=m.evaluate('opencode',sys.argv[2],sys.argv[3]); print(w or '')"
      const result = spawnSync("python3", ["-c", bridge, backend, input.sessionID, directory], { encoding: "utf8", timeout: 10000 })
      if (result.status !== 0 || !result.stdout.trim()) return
      await client.tui.showToast({ body: { title: "Verification warning", message: result.stdout.trim(), variant: "warning" } })
    } catch {}
  },
})
