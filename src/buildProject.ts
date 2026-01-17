import { execSync } from "child_process";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const BUILDER_DIR = path.resolve(__dirname, "../builder");

export function buildProject(projectId: string, projectName: string) {
  console.log(`🚀 Triggering build for ${projectName} (${projectId})`);

  execSync(
    `npx cross-env PROJECT_ID=${projectId} PROJECT_NAME=${projectName} docker compose run --rm flutter-builder`,
    {
      cwd: BUILDER_DIR,
      stdio: "inherit",
    }
  );
}
