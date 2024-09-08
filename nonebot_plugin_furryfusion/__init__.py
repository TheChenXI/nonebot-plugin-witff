import httpx
from nonebot.plugin import on_command
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageEvent

__plugin_meta__ = PluginMetadata(
    name="WITFF",
    description="基于NoneBot2架构的兽聚查询 | When Is The FurryFusion? | 兽聚是什么时候? ",
    usage="使用“/兽聚”查看兽聚列表",
    type="application",
    homepage="https://github.com/TheChenXI/nonebot-plugin-witff",
    supported_adapters={"~onebot.v11"},
)

fusion_activity = on_command("兽聚", priority=10, block=True)

@fusion_activity.handle()
async def fusion_activity_function(event: MessageEvent):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    url = "https://api.furryfusion.net/service/activity"
    
    async with httpx.AsyncClient() as client:
        url_get = await client.get(url, headers=headers)
    
    if url_get.status_code != 200:
        await fusion_activity.finish("失败，稍后再试试吧", at_sender=True)
        return

    url_json = url_get.json()
    data = url_json.get("data", [])

    if not data:
        await fusion_activity.finish("没找到最近的兽聚...xwx", at_sender=True)
        return

    # 提取消息文本，用于关键词搜索
    command_text = str(event.get_message()).strip().split()
    
    if len(command_text) >= 2 and command_text[1] == "搜索":
        keyword = command_text[2] if len(command_text) >= 3 else ""
        if not keyword:
            await fusion_activity.finish("咱好像没有说要查询什么呢?是咱听错了吗ovo", at_sender=True)
            return
        
        # 根据兽聚名称或标题来输出
        filtered_data = [event for event in data if keyword in event["title"] or keyword == event["name"]]

        if not filtered_data:
            await fusion_activity.finish(f"没有找到包含关键词 '{keyword}' 的兽聚呜...", at_sender=True)
            return
    else:
        filtered_data = data

    # 分段/分页
    items_per_page = 3  # 每页显示的兽聚数量
    total_items = len(filtered_data)
    num_pages = (total_items + items_per_page - 1) // items_per_page  # 计算总页数

    page_num = 1  # 默认第一页

    if len(command_text) == 4 and command_text[2].isdigit():
        page_num = max(1, min(num_pages, int(command_text[2])))

    start_index = (page_num - 1) * items_per_page
    end_index = min(start_index + items_per_page, total_items)

    # 输出原结果或搜索结果
    message = f"==== [WITFF?] 第 {page_num}/{num_pages} 页 ====\n"
    for i in range(start_index, end_index):
        event = filtered_data[i]
        title = event["title"]
        name = event["name"]
        state_num = event["state"]
        state_main = ["活动结束", "预告中", "售票中", "活动中", "活动取消"]
        group_json = event.get("groups", [None])[0] if event.get("groups") else "无"
        address = event.get("address", "无地址")
        time_day = event.get("time_day", "未知")
        time_start = event.get("time_start", "未知")
        time_end = event.get("time_end", "未知")
        state = state_main[state_num]
        message += (
            f"\n--------------------\n"
            f"兽聚名称：{title}\n"
            f"兽聚主题：{name}\n"
            f"兽聚状态：{state}\n"
            f"兽聚Q群:{group_json}\n"
            f"兽聚地址：{address}\n"
            f"举办天数：{time_day}天\n"
            f"举办时间：{time_start}~{time_end}\n"
            f"--------------------\n"
        )

    message += f"\n==== [WITFF?] {page_num}/{num_pages} 页 ====\n"
    
    await fusion_activity.finish(message, at_sender=True)

