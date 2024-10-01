def filter_file_links(links):
    """筛选包含文件扩展名的链接"""
    file_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.txt', '.zip']
    return [link for link in links if any(link.endswith(ext) for ext in file_extensions)]
