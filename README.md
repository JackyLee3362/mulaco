# MULACO

**Mu**lti **La**nguage **Co**operate Translation，多语言协作翻译

## 安装

```sh
# 克隆仓库
git clone git@github.com:JackyLee3362/mulaco.git
# 进入项目
cd ./mulaco
```

### 依赖安装

方案一：使用 `poetry`（推荐）

```sh

poetry install
```

方案二：使用 pip + 虚拟环境

```sh
# 创建虚拟环境
python -m venv .venv
# 激活环境
.venv/Scripts/activate
source venv/bin/activate
pip install -r requirements.txt
```

## 运行

```sh
echo 

# 测试 CLI 是否正常
python main.py --help
# 批量运行所有
python main.py run

# 分批运行
# 加载数据
python main.py load
# 修复数据
python main.py pre
# 翻译数据
python main.py translate
# 修复翻译
python main.py post
# 导出
python main.py export


# 开发工具
# 清楚缓存数据
python main.py dev:clear
```

## 配置

### 环境变量

环境变量配置，在根目录创建 `.env` 文件

```ini
PYTHONPATH="src"
TENCENTCLOUD_SECRET_ID="YOUR SECRET ID"
TENCENTCLOUD_SECRET_KEY="YOUR SECRET KEY"
DEEPL_AUTH_KEY="YOUR AUTH KEY"
; 测试环境，定义该变量后
; 会自动读取 config/{MULACO_ENV}/settings.toml 的配置文件
MULACO_ENV="test"
```

### 配置文件

```sh
./config
│  dict.toml     # 用户词典
│  excels.toml   # excel 配置文件
│  lang.toml     # 语言配置
│  settings.toml # 默认配置文件，先读取，
├─dev
│  settings.toml # 如果设置了 MULACO_ENV 属性，则会读取该文件
└─test
   settings.toml
```

## 工作流

1. 编辑配置文件
2. 运行程序
3. 使用 `excel` 打开有链接的文件，点击 数据 - 工作薄链接 - 更改有问题的源
