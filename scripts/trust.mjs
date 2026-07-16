// 一键信任本项目: 把当前项目路径在运行者自己的 ~/.claude.json 里标记为已信任,
// 从而让随仓库分发的 .claude/settings.json 里声明的放行权限直接生效, 免去首次打开时的信任弹窗。
//
// 为什么改 ~/.claude.json 而不是项目内文件: "是否信任某目录" 是 Claude Code 的
// 用户级状态(每台机器、每个人各一份), 天然无法随仓库共享, 只能由本机脚本写入。
// 权限声明(allow/ask/defaultMode)才是项目级的, 已放在 .claude/settings.json 里提交。
//
// 设计取舍: 只翻转 hasTrustDialogAccepted 这一个开关, 不动其它任何字段; 写前必做备份、
// 原子落盘; 已是 true 则直接跳过。幂等、可回滚、不吞异常。

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const TRUST_FLAG = "hasTrustDialogAccepted";

// 项目根 = 本脚本所在 scripts/ 的上一级。用脚本自身位置定位, 不依赖调用时的工作目录,
// 这样无论从哪里执行(双击 bat / 任意目录 sh)都指向正确的项目。
const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(scriptDir, "..");

// ~/.claude.json 的 key 统一用正斜杠(与 Claude Code 自身写入的格式一致), 反斜杠会导致查不到。
const normalize = (p) => p.split(path.sep).join("/").replace(/\/+$/, "");
const projectKey = normalize(projectRoot);

const configPath = path.join(os.homedir(), ".claude.json");

function fail(msg) {
  console.error(`[FAIL] ${msg}`);
  process.exit(1);
}

// 读取(或初始化)配置。文件不存在说明本机还没跑过 Claude Code, 建一个最小骨架即可,
// 后续 Claude Code 首次启动会自动补齐其余默认字段。
let config;
let fileExisted = fs.existsSync(configPath);
if (fileExisted) {
  let raw;
  try {
    raw = fs.readFileSync(configPath, "utf8");
  } catch (err) {
    fail(`读取 ${configPath} 失败: ${err.message}`);
  }
  try {
    config = JSON.parse(raw);
  } catch (err) {
    // 解析失败绝不覆盖, 避免毁掉用户既有配置。
    fail(`${configPath} 不是合法 JSON, 已中止以免损坏原文件: ${err.message}`);
  }
} else {
  config = {};
}

if (typeof config !== "object" || config === null || Array.isArray(config)) {
  fail(`${configPath} 顶层不是对象, 已中止。`);
}
if (typeof config.projects !== "object" || config.projects === null) {
  config.projects = {};
}

// 大小写不敏感地找已有条目(Windows 盘符/路径大小写可能不同), 命中就复用那个 key,
// 避免因大小写差异生成重复条目导致信任不生效。
const existingKey = Object.keys(config.projects).find(
  (k) => normalize(k).toLowerCase() === projectKey.toLowerCase(),
);
const targetKey = existingKey ?? projectKey;

if (typeof config.projects[targetKey] !== "object" || config.projects[targetKey] === null) {
  config.projects[targetKey] = {};
}

if (config.projects[targetKey][TRUST_FLAG] === true) {
  console.log(`[SKIP] 该项目已是信任状态, 无需改动: ${targetKey}`);
  console.log(`[INFO] 权限声明见 .claude/settings.json, 打开项目即自动生效。`);
  process.exit(0);
}

// 改动前先备份(仅当原文件存在)。备份名带时间戳, 便于回滚。
if (fileExisted) {
  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  const backupPath = `${configPath}.bak-${stamp}`;
  try {
    fs.copyFileSync(configPath, backupPath);
    console.log(`[INFO] 已备份原配置 -> ${backupPath}`);
  } catch (err) {
    fail(`备份失败, 已中止未做任何修改: ${err.message}`);
  }
}

config.projects[targetKey][TRUST_FLAG] = true;

// 原子落盘: 先写同目录临时文件再 rename, 避免中途崩溃留下半截文件。
const serialized = `${JSON.stringify(config, null, 2)}\n`;
const tmpPath = `${configPath}.tmp-${process.pid}`;
try {
  fs.writeFileSync(tmpPath, serialized, "utf8");
  fs.renameSync(tmpPath, configPath);
} catch (err) {
  try {
    fs.rmSync(tmpPath, { force: true });
  } catch {
    // 清理失败不影响主流程, 忽略。
  }
  fail(`写入 ${configPath} 失败: ${err.message}`);
}

console.log(`[PASS] 已将本项目标记为信任: ${targetKey}`);
console.log(`[INFO] 生效说明: 请在关闭该项目的 Claude Code 后再运行本脚本, 下次打开即免信任弹窗、`);
console.log(`       并自动应用 .claude/settings.json 中声明的放行权限。`);
