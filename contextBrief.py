import re

def parse_structured_text(text):
    # 分割主条目（支持数字开头的中文/英文编号）
    main_pattern = r'\n(\d+[\.。、]*[：: ]?.*?)(?=\n\d+[\.。、]|$)'
    main_items = re.findall(main_pattern, text, re.DOTALL)
    
    result = []
    for item in main_items:
        # 提取主条目编号和内容
        header_match = re.match(r'(\d+)[\.。、]*[：: ]?(.*)', item.strip(), re.DOTALL)
        if not header_match:
            continue
            
        num, content = header_match.groups()
        content = content.strip()
        
        # 检测子条目（带括号的数字编号）
        sub_pattern = r'[\(（](\d+)[\)）]\s*(.*?)(?=[\(（]\d+[\)）]|；|$)'
        sub_matches = re.findall(sub_pattern, content, re.DOTALL)
        
        if sub_matches:  # 有子条目
            sub_list = [sub[1].strip() for sub in sub_matches]
            # 提取主条目标题（去掉冒号后的内容）
            title = re.split(r'[：:]', content)[0].strip()
            result.append([f"{title}", sub_list])
        else:            # 无子条目
            result.append(content)
    
    return result

#############################################
# 使用示例
text = """
1.【新思想引领新征程】经济大省挑大梁 为高质量发展注入强大动力；
2.教育部直属高校工作咨询委员会第三十一次全体会议在京召开 丁薛祥出席会议并讲话；
3.中办印发《通知》在全党开展深入贯彻中央八项规定精神学习教育；
4.【真抓实干 打开改革发展新天地】搭建创新平台 天津加速科技成果转化 以“中试平台”为抓手 四川深度融合创新链产业链；
5.经济运行起步平稳 发展态势向新向好；
6.我国将多措并举大力提振消费；
7.【活力中国调研行】数字经济快速增长背后的能量密码；
8.踏青赏花 乐享春日好时光；
9.国内联播快讯：
（1）新版《消费品售后服务方法与要求》国家标准5月1日起实施；
（2）2月份我国商品房销售价格持续回稳；
（3）2025年全国精品首发季活动在上海启动；
（4）乌鲁木齐海关出台二十项新举措优化口岸营商环境；
（5）我国成功发射云遥一号55-60星等8颗卫星；
（6）942人入选第六批国家级非物质文化遗产代表性传承人；
（7）总台大型文化节目《中国书法大会》（第二季）启播；
10.美军连续第二天空袭也门 胡塞武装称打击美航母舰队；
11.俄称在多方向发动攻势 乌称采取措施阻止俄军进攻；
12.国际联播快讯：
（1）美恶劣天气已致40人死亡 大量用户断电；
（2）欧洲央行官员称美关税政策致经济不稳定；
（3）澳大利亚珀斯附近林火蔓延 道路封闭。
"""

structured_data = parse_structured_text(text)

# 打印结构化结果
for i, item in enumerate(structured_data, 1):
    if isinstance(item, list):
        print(f"{item[0]}")
        for j, sub in enumerate(item[1], 1):
            print(f"  └─({j}) {sub}")
    else:
        print(item)