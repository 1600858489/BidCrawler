# Web Crawler Application

这是一个基于 PyQt5 的简单网页查询工具工具，允许用户输入 URL，提取网页中的文件链接并展示结果。该项目使用面向对象编程（OOP）思想，将功能模块化，方便代码重用和维护。

## 目录结构

```
web_crawler/
├── core/
│   ├── __init__.py
│   ├── algorithm.py           # 包含通用的逻辑与算法
│   └── history_manager.py     # 历史记录管理
├── crawler/
│   ├── __init__.py
│   └── crawler.py             # 查询工具核心代码
├── ui/
│   ├── __init__.py
│   └── main_window.py         # 页面核心代码
└── main.py                    # 主程序入口
```

- **`core/`**：包含与逻辑和算法相关的代码。
  - `algorithm.py`：实现了文件链接筛选的逻辑。
  - `history_manager.py`：管理已经查询的 URL 记录。
  
- **`crawler/`**：包含查询工具的核心代码。
  - `crawler.py`：包含用于抓取网页和提取链接的逻辑。

- **`ui/`**：包含应用程序的界面代码。
  - `main_window.py`：实现了整个 GUI 界面和用户交互。

- **`main.py`**：主程序入口，启动应用程序。

## 功能

- 用户可以输入目标网页的 URL或选择已优化的 URL。
- 结果展示在 UI 界面中，用户可以看到提取到的文件链接。
- 已经查询过的 URL 会被记录在历史记录中，并避免重复查询。

## 安装依赖

在运行此项目之前，您需要安装以下依赖项。可以使用 `pip` 进行安装：

```sh
pip install -r requirements.txt
```

## 运行程序

要运行该程序，请进入项目的根目录，并执行以下命令：

```sh
python main.py
```

## 程序打包

如果需要将程序打包为可执行文件，可以使用 `PyInstaller` 工具。

```sh
pip install pyinstaller
```

然后，在项目根目录下执行以下命令：

```sh
pyinstaller --onefile --windowed main.py
```

该命令将生成一个名为 `main.exe` 的可执行文件。

如果希望打包到特定位置，可以使用 `--distpath` 参数指定。
```sh
pyinstaller --onefile --windowed --distpath "./pack" --workpath "./pack/build" --specpath "./pack" --icon="F:\python_projcet\BidCrawler\favicon.ico" --name "BidCrawler" main.py
```


## 项目实现要点

1. **模块化和解耦**：使用 OOP 编程，将不同功能模块化。查询工具核心代码与界面代码、历史记录管理等分离，方便后期的维护和扩展。

2. **代码说明**：
   - **WebCrawler**：查询工具的核心类，负责抓取网页内容并提取链接。
   - **HistoryManager**：管理已经查询过的 URL，避免重复查询。
   - **filter_file_links**：用于筛选网页中的文件链接。
   - **WebCrawlerApp**：基于 PyQt5 实现的 GUI 应用程序。

3. **灵活性和可维护性**：这种结构使得每个部分的功能清晰独立，便于进一步扩展。例如，如果要更改查询工具逻辑，只需修改 `crawler.py`，而无需改动界面代码；同样地，如果要调整历史记录管理的方式，可以在 `history_manager.py` 中进行操作。

## 未来扩展

- 增加多线程查询功能，提高查询速度。
- 添加对更复杂文件类型的支持。
- 使用数据库保存历史记录以替代内存保存。
- 增加错误日志记录功能，方便调试和维护。

## 许可证

MIT License
