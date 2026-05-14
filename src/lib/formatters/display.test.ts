import assert from "node:assert/strict";

import { getEditorSaveStatusLabel, getFontFamilyLabel } from "@/lib/formatters/display";

assert.equal(getEditorSaveStatusLabel("saved"), "已保存");
assert.equal(getFontFamilyLabel("Microsoft YaHei"), "微软雅黑");
assert.equal(getFontFamilyLabel("KaiTi"), "楷体");
assert.equal(getFontFamilyLabel("sans-serif"), "无衬线");
