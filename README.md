# sync-template

`sync-template` 是一个用于管理和同步基于模板开发的项目的 CLI 工具。它可以帮助你在模板项目更新后，轻松地将更新合并到你的现有项目中，同时通过 `.syncignore` 保护你的本地修改。

## 核心功能

- **快速初始化**: 使用 `git clone --depth 1` 从模板仓库快速创建新项目。
- **自动配置**: 自动将模板仓库设置为名为 `template` 的远程仓库（remote）。
- **智能同步**: 通过 `git fetch` 和 `git merge` 获取模板更新。
- **.syncignore 保护**: 在合并后自动应用忽略规则，确保指定的文件或目录完全保持本地状态（支持递归目录）。
- **安全检查**: 在同步前自动检查工作区是否有未提交或未追踪的文件，防止意外覆盖。

## 安装

确保你的系统已安装 Python 3.13+ 和 Git。

使用 pip 安装（发布后）：
```bash
pip install sync-template
```

或者通过源码安装（使用 Poetry）：
```bash
git clone https://github.com/your-username/sync-template.git
cd sync-template
poetry install
```

## 使用方法

### 1. 初始化新项目

从一个 Git 模板仓库创建一个新项目：

```bash
sync-template init https://github.com/user/my-python-template.git my-new-project
```

这会：
- 将模板克隆到 `my-new-project`。
- 将远程 `origin` 重命名/设置为 `template`。

### 2. 配置忽略文件

在项目根目录下创建 `.syncignore` 文件。其语法与 `.gitignore` 相同。

例如：
```text
# 忽略配置文件
config.json
# 忽略整个内容目录（包括新增、修改和删除）
content/
# 忽略特定的本地脚本
scripts/local_only.sh
```

### 3. 同步更新

当模板仓库有更新时，在项目根目录运行：

```bash
sync-template sync
```

默认同步 `main` 分支。如果需要同步其他分支，可以使用 `--branch` 参数：

```bash
sync-template sync --branch develop
```

## 工作原理

1. **工作流检查**: 确保当前分支没有未提交的改动。
2. **获取更新**: 执行 `git fetch template`。
3. **合并尝试**: 执行 `git merge --no-commit template/<branch>`。
4. **应用忽略**:
   - 遍历 `.syncignore` 匹配的所有路径。
   - 如果路径在同步前已存在，则使用 `git checkout HEAD` 恢复其内容，并自动解决冲突。
   - 如果路径是模板新增的，则物理删除文件并从 Git 索引中移除。
   - **自动清理**: 递归清理因删除操作产生的空文件夹。
5. **完成**: 提示用户查看合并结果并提交。

## 开发与贡献

该项目使用 [Poetry](https://python-poetry.org/) 进行包管理。

- **运行测试**: `poetry run pytest`
- **代码规范检查**: `poetry run ruff check .`
- **代码格式化**: `poetry run ruff format .`

## 开源协议

本项目采用 [MIT License](LICENSE) 协议。
