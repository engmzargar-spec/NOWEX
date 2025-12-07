// تست import کردن از packages
try {
  const ui = require("./packages/shared-ui/dist/index.js");
  console.log("✅ shared-ui import successful");
  console.log("Exports:", Object.keys(ui));
} catch (error) {
  console.log("❌ shared-ui import failed:", error.message);
}

try {
  const api = require("./packages/shared-api/dist/index.js");
  console.log("✅ shared-api import successful");
  console.log("Exports:", Object.keys(api));
} catch (error) {
  console.log("❌ shared-api import failed:", error.message);
}
