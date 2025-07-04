import random
import json
import os
from openrouter_client import call_llm
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum

class Suit(Enum):
    MAJOR_ARCANA = "大阿卡纳"
    WANDS = "权杖"
    CUPS = "圣杯"
    SWORDS = "宝剑"
    PENTACLES = "星币"

@dataclass
class TarotCard:
    name: str
    suit: Suit
    number: Optional[int]
    keywords: List[str]
    upright_meaning: str
    reversed_meaning: str
    description: str

class TarotDeck:
    def __init__(self):
        self.cards = self._create_deck()
        self.shuffled_deck = self.cards.copy()
        self.shuffle()
    
    def _create_deck(self) -> List[TarotCard]:
        """创建完整的78张塔罗牌"""
        cards = []
        
        # 大阿卡纳 (22张)
        major_arcana = [
            ("愚者", ["新开始", "冒险", "纯真"], "新的开始，充满可能性的旅程", "鲁莽，缺乏方向"),
            ("魔术师", ["意志力", "创造", "技能"], "运用意志力实现目标", "操控，滥用权力"),
            ("女祭司", ["直觉", "神秘", "内在智慧"], "倾听内心声音，相信直觉", "忽视直觉，缺乏内省"),
            ("皇后", ["丰饶", "母性", "创造力"], "丰富的创造力和nurturing能量", "过度依赖，创造力受阻"),
            ("皇帝", ["权威", "结构", "控制"], "建立秩序和稳定的基础", "专制，过度控制"),
            ("教皇", ["传统", "精神指导", "学习"], "寻求精神指导和传统智慧", "教条主义，拒绝新思想"),
            ("恋人", ["选择", "关系", "和谐"], "重要的选择和关系和谐", "关系冲突，错误选择"),
            ("战车", ["意志力", "控制", "胜利"], "通过意志力克服障碍", "失控，缺乏方向"),
            ("力量", ["内在力量", "勇气", "耐心"], "温和的力量和内在勇气", "软弱，缺乏自信"),
            ("隐者", ["内省", "寻找", "指导"], "内在寻找和精神指导", "孤立，拒绝帮助"),
            ("命运之轮", ["变化", "命运", "机会"], "生命的循环和转折点", "厄运，失控的变化"),
            ("正义", ["公正", "平衡", "真理"], "公正的判断和道德平衡", "不公正，偏见"),
            ("倒吊人", ["牺牲", "等待", "新视角"], "通过牺牲获得新的视角", "无意义的牺牲，拖延"),
            ("死神", ["转变", "结束", "重生"], "重大转变和新的开始", "抗拒变化，停滞"),
            ("节制", ["平衡", "耐心", "调和"], "寻找平衡中和庸之道", "不耐烦，极端"),
            ("恶魔", ["束缚", "诱惑", "物质主义"], "被物质欲望束缚", "摆脱束缚，精神觉醒"),
            ("塔", ["突然变化", "启示", "解放"], "突然的觉醒和解放", "避免必要的变化"),
            ("星星", ["希望", "灵感", "指导"], "希望和精神指导", "绝望，失去信心"),
            ("月亮", ["幻象", "直觉", "潜意识"], "面对幻象和潜意识恐惧", "克服恐惧，看清真相"),
            ("太阳", ["成功", "喜悦", "活力"], "成功、喜悦和生命力", "过度自信，延迟的成功"),
            ("审判", ["重生", "觉醒", "宽恕"], "精神觉醒和重新开始", "自我怀疑，拒绝成长"),
            ("世界", ["完成", "成就", "整合"], "目标达成和圆满结束", "缺乏闭合，未完成的事业")
        ]
        
        for i, (name, keywords, upright, reversed) in enumerate(major_arcana):
            cards.append(TarotCard(
                name=name,
                suit=Suit.MAJOR_ARCANA,
                number=i,
                keywords=keywords,
                upright_meaning=upright,
                reversed_meaning=reversed,
                description=f"大阿卡纳第{i}张牌，代表{keywords[0]}的能量"
            ))
        
        # 小阿卡纳 (56张)
        suits_data = {
            Suit.WANDS: ("权杖", "火元素，代表激情、创造力和行动"),
            Suit.CUPS: ("圣杯", "水元素，代表情感、直觉和关系"),
            Suit.SWORDS: ("宝剑", "风元素，代表思想、沟通和冲突"),
            Suit.PENTACLES: ("星币", "土元素，代表物质、金钱和实用性")
        }
        
        court_cards = ["侍从", "骑士", "王后", "国王"]
        
        for suit, (suit_name, suit_desc) in suits_data.items():
            # 数字牌 1-10
            for num in range(1, 11):
                cards.append(TarotCard(
                    name=f"{suit_name}{num}",
                    suit=suit,
                    number=num,
                    keywords=["开始", "能量", "行动"] if num == 1 else ["发展", "进程", "变化"],
                    upright_meaning=f"{suit_name}的{num}号牌，代表该元素的特定能量",
                    reversed_meaning=f"能量受阻或过度表现",
                    description=f"{suit_desc}的数字牌"
                ))
            
            # 宫廷牌
            for court in court_cards:
                cards.append(TarotCard(
                    name=f"{suit_name}{court}",
                    suit=suit,
                    number=None,
                    keywords=["人物", "性格", "影响"],
                    upright_meaning=f"代表{suit_name}元素的{court}特质",
                    reversed_meaning=f"{court}特质的负面表现",
                    description=f"{suit_desc}的宫廷牌"
                ))
        
        return cards
    
    def shuffle(self):
        """洗牌"""
        random.shuffle(self.shuffled_deck)
    
    def draw_card(self) -> TarotCard:
        """抽取一张牌"""
        if not self.shuffled_deck:
            self.shuffled_deck = self.cards.copy()
            self.shuffle()
        return self.shuffled_deck.pop()
    
    def draw_cards(self, count: int) -> List[TarotCard]:
        """抽取多张牌"""
        return [self.draw_card() for _ in range(count)]

class TarotReading:
    def __init__(self, cards: List[TarotCard], spread_type: str, spread_description: str, question: str = ""):
        self.cards = cards
        self.spread_type = spread_type
        self.spread_description = spread_description
        self.question = question
        self.reversed_cards = [random.choice([True, False]) for _ in cards]
        self.timestamp = datetime.now()
    
    def get_card_meaning(self, index: int) -> str:
        """获取指定位置牌的含义"""
        card = self.cards[index]
        is_reversed = self.reversed_cards[index]
        
        meaning = card.reversed_meaning if is_reversed else card.upright_meaning
        position = "逆位" if is_reversed else "正位"
        
        return f"{card.name} ({position}): {meaning}"
    
    def format_reading(self) -> str:
        """格式化占卜结果"""
        result = f"\n=== 塔罗牌占卜结果 ===\n"
        result += f"时间: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        result += f"牌阵类型: {self.spread_type}\n"
        result += f"牌阵说明: {self.spread_description}\n"
        if self.question:
            result += f"问题: {self.question}\n"
        result += f"\n抽到的牌:\n"
        
        for i, card in enumerate(self.cards):
            position = "逆位" if self.reversed_cards[i] else "正位"
            result += f"{i+1}. {card.name} ({position})\n"
        
        return result
    
    def to_dict(self) -> dict:
        """转换为字典格式用于保存"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "question": self.question,
            "spread_type": self.spread_type,
            "spread_description": self.spread_description,
            "cards": [
                {
                    "name": card.name,
                    "suit": card.suit.value,
                    "position": "逆位" if self.reversed_cards[i] else "正位",
                    "meaning": card.reversed_meaning if self.reversed_cards[i] else card.upright_meaning
                }
                for i, card in enumerate(self.cards)
            ]
        }

class SpreadRecommender:
    """牌阵推荐器"""
    
    def __init__(self):
        self.spreads = {
            "single_card": {
                "name": "单张牌指引",
                "cards": 1,
                "description": "快速获得当下指导，适合日常决策和简单问题",
                "positions": ["当前指引"]
            },
            "three_card_time": {
                "name": "时间三张牌",
                "cards": 3,
                "description": "了解过去、现在、未来的发展趋势",
                "positions": ["过去", "现在", "未来"]
            },
            "three_card_situation": {
                "name": "情况三张牌",
                "cards": 3,
                "description": "分析问题的不同角度",
                "positions": ["情况", "行动", "结果"]
            },
            "love_relationship": {
                "name": "爱情关系牌阵",
                "cards": 5,
                "description": "深入了解感情状况和发展方向",
                "positions": ["你的感受", "对方的感受", "关系现状", "挑战", "未来发展"]
            },
            "career_guidance": {
                "name": "事业指导牌阵",
                "cards": 6,
                "description": "全面分析职业发展和工作状况",
                "positions": ["当前状况", "优势", "挑战", "机会", "建议行动", "未来前景"]
            },
            "decision_making": {
                "name": "决策分析牌阵",
                "cards": 7,
                "description": "帮助做出重要决定",
                "positions": ["当前情况", "选择A", "选择A结果", "选择B", "选择B结果", "外在影响", "最佳建议"]
            },
            "celtic_cross": {
                "name": "凯尔特十字",
                "cards": 10,
                "description": "最全面的牌阵，深度分析复杂问题",
                "positions": ["当前状况", "挑战", "远因", "近因", "可能结果", "近期发展", "你的态度", "外在影响", "内心期望", "最终结果"]
            },
            "year_forecast": {
                "name": "年度运势",
                "cards": 12,
                "description": "预测一年中每个月的运势发展",
                "positions": [f"{i+1}月" for i in range(12)]
            }
        }
    
    def get_recommendations(self, question: str) -> List[str]:
        """根据问题推荐合适的牌阵"""
        prompt = f"""作为专业塔罗牌占卜师，请根据以下问题推荐最合适的3个牌阵类型。
    
        用户问题：{question}
    
        可选牌阵：
        1. 单张牌指引 - 快速获得当下指导，适合日常决策和简单问题
        2. 时间三张牌 - 了解过去、现在、未来的发展趋势
        3. 情况三张牌 - 分析问题的不同角度
        4. 爱情关系牌阵 - 深入了解感情状况和发展方向
        5. 事业指导牌阵 - 全面分析职业发展和工作状况
        6. 决策分析牌阵 - 帮助做出重要决定
        7. 凯尔特十字 - 最全面的牌阵，深度分析复杂问题
        8. 年度运势 - 预测一年中每个月的运势发展
    
        请按优先级顺序推荐3个最合适的牌阵，并简要说明推荐理由。
        格式：
        1. [牌阵名称] - [推荐理由]
        2. [牌阵名称] - [推荐理由]
        3. [牌阵名称] - [推荐理由]"""
        
        try:
            response = call_llm(prompt)
            return self._parse_recommendations(response)
        except Exception as e:
            print(f"LLM推荐失败: {e}")
            return ["single_card", "three_card_time", "three_card_situation"]
    
    def _parse_recommendations(self, response: str) -> List[str]:
        """解析LLM推荐结果"""
        recommendations = []
        name_mapping = {
            "单张牌指引": "single_card",
            "时间三张牌": "three_card_time",
            "情况三张牌": "three_card_situation",
            "爱情关系牌阵": "love_relationship",
            "事业指导牌阵": "career_guidance",
            "决策分析牌阵": "decision_making",
            "凯尔特十字": "celtic_cross",
            "年度运势": "year_forecast"
        }
        
        for name, key in name_mapping.items():
            if name in response:
                recommendations.append(key)
        
        # 确保至少有3个推荐
        if len(recommendations) < 3:
            defaults = ["single_card", "three_card_time", "three_card_situation"]
            for default in defaults:
                if default not in recommendations:
                    recommendations.append(default)
                if len(recommendations) >= 3:
                    break
        
        return recommendations[:3]

class LLMTarotInterpreter:
    def __init__(self, model: str = "deepseek/deepseek-chat-v3-0324"):
        self.model = model
    
    def interpret_reading(self, reading: TarotReading) -> str:
        """使用LLM解读塔罗牌"""
        prompt = self._build_prompt(reading)
        
        try:
            response = call_llm(prompt, model=self.model)
            return response
        except Exception as e:
            return f"未能成功获取解读结果: {str(e)}"
    
    def _build_prompt(self, reading: TarotReading) -> str:
        """构建LLM提示词"""
        cards_info = []
        for i, card in enumerate(reading.cards):
            position = "逆位" if reading.reversed_cards[i] else "正位"
            meaning = card.reversed_meaning if reading.reversed_cards[i] else card.upright_meaning
            position_name = reading.spread_description.split("，")[0] if i == 0 else f"位置{i+1}"
            cards_info.append(f"{position_name}: {card.name} ({position}) - {meaning}")
        
        prompt = f"""作为一位经验丰富的塔罗牌占卜师，请为以下塔罗牌占卜结果提供详细而有洞察力的解读：

问题：{reading.question if reading.question else '一般性指导'}
牌阵：{reading.spread_type}
牌阵说明：{reading.spread_description}

抽到的牌：
{chr(10).join(cards_info)}

请提供：
1. 整体解读和核心信息
2. 每张牌在其位置上的具体含义
3. 牌与牌之间的关联和互动
4. 针对问题的具体建议和指导
5. 需要注意的事项或警示

请用温和、智慧且富有洞察力的语调进行解读，帮助问卜者获得真正的指导。"""
        
        return prompt

class ResultSaver:
    """结果保存器"""
    
    def __init__(self, save_dir: str = "answers"):
        self.save_dir = save_dir
        self._ensure_dir_exists()
    
    def _ensure_dir_exists(self):
        """确保保存目录存在"""
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
    
    def save_reading(self, reading: TarotReading, interpretation: str = "") -> str:
        """保存占卜结果"""
        timestamp = reading.timestamp.strftime("%Y%m%d_%H%M%S")
        
        # 保存JSON格式（用于程序处理）
        json_filename = f"tarot_reading_{timestamp}.json"
        json_filepath = os.path.join(self.save_dir, json_filename)
        
        # 保存美观的文本格式（用于用户阅读）
        txt_filename = f"tarot_reading_{timestamp}.txt"
        txt_filepath = os.path.join(self.save_dir, txt_filename)
        
        try:
            # 保存JSON格式
            data = reading.to_dict()
            data["interpretation"] = interpretation
            
            with open(json_filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 保存美观的文本格式
            formatted_report = self._generate_beautiful_report(reading, interpretation)
            with open(txt_filepath, 'w', encoding='utf-8') as f:
                f.write(formatted_report)
            
            return txt_filepath  # 返回文本文件路径
            
        except Exception as e:
            print(f"保存失败: {e}")
            return ""
    
    def _generate_beautiful_report(self, reading: TarotReading, interpretation: str) -> str:
        """生成美观的文本报告"""
        report = []
        
        # 标题和分隔线
        report.append("🔮" + "="*60 + "🔮")
        report.append("                    塔罗牌占卜报告")
        report.append("🔮" + "="*60 + "🔮")
        report.append("")
        
        # 基本信息
        report.append("📅 占卜时间: " + reading.timestamp.strftime("%Y年%m月%d日 %H:%M:%S"))
        report.append("❓ 占卜问题: " + (reading.question or "一般性指导"))
        report.append("🎯 使用牌阵: " + reading.spread_type)
        report.append("📝 牌阵说明: " + reading.spread_description)
        report.append("")
        
        # 抽牌结果
        report.append("🃏" + "-"*58 + "🃏")
        report.append("                      抽牌结果")
        report.append("🃏" + "-"*58 + "🃏")
        report.append("")
        
        for i, card in enumerate(reading.cards, 1):
            position_desc = "逆位 🔄" if reading.reversed_cards[i-1] else "正位 ⬆️"
            meaning = card.reversed_meaning if reading.reversed_cards[i-1] else card.upright_meaning
            
            report.append(f"第{i}张牌: {card.name} ({card.suit.value})")
            report.append(f"  状态: {position_desc}")
            report.append(f"  含义: {meaning}")
            report.append("")
        
        # AI解读部分
        if interpretation:
            report.append("🤖" + "-"*58 + "🤖")
            report.append("                      AI 深度解读")
            report.append("🤖" + "-"*58 + "🤖")
            report.append("")
            
            # 处理解读文本，保持原有的markdown格式但增加可读性
            interpretation_lines = interpretation.split('\n')
            for line in interpretation_lines:
                if line.strip():
                    report.append(line)
                else:
                    report.append("")
        
        # 结尾
        report.append("")
        report.append("✨" + "="*58 + "✨")
        report.append("                 愿智慧与您同在")
        report.append("✨" + "="*58 + "✨")
        
        return "\n".join(report)

class TarotApp:
    def __init__(self):
        self.deck = TarotDeck()
        self.interpreter = LLMTarotInterpreter()
        self.recommender = SpreadRecommender()
        self.saver = ResultSaver()
    
    def run(self):
        """运行塔罗牌程序"""
        print("🔮 欢迎来到智能塔罗牌占卜世界 🔮")
        print("="*50)
        
        while True:
            try:
                if not self._main_flow():
                    break
            except KeyboardInterrupt:
                print("\n\n感谢使用，愿智慧与您同在 ✨")
                break
            except Exception as e:
                print(f"❌ 发生错误: {str(e)}")
    
    def _main_flow(self) -> bool:
        """主要流程"""
        print("\n" + "="*50)
        print("🌟 开始新的塔罗牌占卜")
        
        # 1. 获取问题
        question = self._get_question()
        if question.lower() in ['quit', 'exit', '退出', 'q']:
            print("感谢使用塔罗牌占卜程序！愿智慧与您同在 ✨")
            return False
        
        # 2. LLM推荐牌阵
        print("\n🤖 AI正在分析您的问题并推荐合适的牌阵...")
        recommended_spreads = self._get_spread_recommendations(question)
        
        # 3. 用户选择牌阵
        selected_spread = self._select_spread(recommended_spreads)
        if not selected_spread:
            return True
        
        # 4. 执行占卜
        reading = self._perform_reading(question, selected_spread)
        
        # 5. LLM解读
        interpretation = self._get_interpretation(reading)
        
        # 6. 保存结果
        self._save_results(reading, interpretation)
        
        # 7. 询问是否继续
        return self._ask_continue()
    
    def _get_question(self) -> str:
        """获取用户问题"""
        print("\n💭 请输入您想要占卜的问题：")
        print("（可以是关于爱情、事业、人际关系、决策等任何方面）")
        print("（输入 'quit' 或 'exit' 退出程序）")
        
        question = input("\n您的问题: ").strip()
        
        if not question:
            question = "请为我提供当下的指导"
            print(f"使用默认问题: {question}")
        
        return question
    
    def _get_spread_recommendations(self, question: str) -> List[str]:
        """获取牌阵推荐"""
        try:
            return self.recommender.get_recommendations(question)
        except Exception as e:
            print(f"推荐系统出错: {e}")
            return ["single_card", "three_card_time", "three_card_situation"]
    
    def _select_spread(self, recommended_spreads: List[str]) -> Optional[str]:
        """选择牌阵"""
        print("\n🎯 根据您的问题，AI推荐以下牌阵：")
        print("="*40)
        
        # 显示推荐的牌阵
        for i, spread_key in enumerate(recommended_spreads, 1):
            spread = self.recommender.spreads[spread_key]
            print(f"{i}. {spread['name']} ({spread['cards']}张牌) ⭐")
            print(f"   {spread['description']}")
            print()
        
        # 显示所有牌阵的完整列表
        print("\n📋 所有可选牌阵：")
        all_spreads = list(self.recommender.spreads.keys())
        
        for i, spread_key in enumerate(all_spreads, 1):
            spread = self.recommender.spreads[spread_key]
            star = " ⭐" if spread_key in recommended_spreads else ""
            print(f"{i}. {spread['name']} ({spread['cards']}张牌){star}")
        
        print("\n0. 返回主菜单")
        
        while True:
            try:
                choice = input("\n请选择牌阵 (输入数字): ").strip()
                
                if choice == "0":
                    return None
                
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(all_spreads):
                    return all_spreads[choice_num - 1]
                else:
                    print("❌ 无效选择，请重新输入")
                    
            except ValueError:
                print("❌ 请输入有效数字")
    
    def _perform_reading(self, question: str, spread_key: str) -> TarotReading:
        """执行占卜"""
        spread = self.recommender.spreads[spread_key]
        
        print(f"\n🔮 开始 {spread['name']} 占卜")
        print(f"牌阵说明: {spread['description']}")
        
        print("\n🌟 正在洗牌...")
        self.deck.shuffle()
        
        print("✨ 正在抽牌...")
        cards = self.deck.draw_cards(spread['cards'])
        
        reading = TarotReading(
            cards=cards,
            spread_type=spread['name'],
            spread_description=spread['description'],
            question=question
        )
        
        # 显示抽牌结果
        print(reading.format_reading())
        
        # 显示牌阵位置说明
        if 'positions' in spread:
            print("\n📍 牌阵位置说明:")
            for i, position in enumerate(spread['positions']):
                card = cards[i]
                position_desc = "逆位" if reading.reversed_cards[i] else "正位"
                print(f"{i+1}. {position}: {card.name} ({position_desc})")
        
        return reading
    
    def _get_interpretation(self, reading: TarotReading) -> str:
        """获取解读"""
        if input("\n🤖 是否需要AI详细解读？(y/n): ").lower().startswith('y'):
            print("\n🔍 AI正在深度解读中，请稍候...")
            interpretation = self.interpreter.interpret_reading(reading)
            print("\n" + "="*50)
            print("🎭 AI塔罗牌解读")
            print("="*50)
            print(interpretation)
            return interpretation
        return ""
    
    def _save_results(self, reading: TarotReading, interpretation: str):
        """保存结果"""
        filepath = self.saver.save_reading(reading, interpretation)
        if filepath:
            print(f"\n💾 占卜结果已保存到: {filepath}")
            
            # 询问是否立即查看报告
            if input("\n📖 是否立即查看完整报告？(y/n): ").lower().startswith('y'):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    print("\n" + "="*80)
                    print(content)
                    print("="*80)
                except Exception as e:
                    print(f"读取报告失败: {e}")
    
    def _ask_continue(self) -> bool:
        """询问是否继续"""
        print("\n" + "="*50)
        continue_choice = input("是否继续新的占卜？(y/n): ").lower()
        return continue_choice.startswith('y')

def get_all_spreads(self):
    """获取所有可用的牌阵"""
    return self.spreads

def main():
    """主函数"""
    app = TarotApp()
    app.run()

if __name__ == "__main__":
    main()

