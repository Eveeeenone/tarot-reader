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
            ("愚者", ["新开始", "冒险", "纯真", "自发性", "无限可能"], 
             "代表新的开始，充满无限可能性。鼓励以纯真、开放的心态去探索未知，勇敢地踏上新的旅程。在爱情中，可能预示着一段轻松、无拘无束的新关系。在事业上，是尝试新项目或转换跑道的好时机。", 
             "代表鲁莽、轻率的行动，缺乏计划和远见。可能因为过于冲动而忽视了潜在的风险，或在逃避责任。建议在行动前三思，并对自己的选择负责。"),
            
            ("魔术师", ["意志力", "创造", "显化", "技能", "专注"], 
             "代表强大的意志力和创造力，能够将想法转化为现实。拥有实现目标所需的所有工具和技能。在事业上，表示能够掌控局面，发挥才能。在个人成长中，是学习新技能、实现潜能的绝佳时机。", 
             "代表滥用能力、操控他人或欺骗。可能表示技能不足却夸大其词，或将才智用于不正当的目的。需要警惕被表象迷惑，或自己陷入自欺欺人的境地。"),
            
            ("女祭司", ["直觉", "神秘", "潜意识", "内在智慧", "秘密"], 
             "代表直觉、潜意识和内在的智慧。鼓励向内探索，倾听自己内心的声音。有些事情需要静待时机，不能强求。在人际关系中，表示需要更深的理解和洞察力。在决策时，应相信自己的直觉。", 
             "代表忽视直觉、压抑情感或与内心失去连接。可能因为过度依赖逻辑分析而忽略了重要的感受。也可能表示有秘密被揭露，或对情况有错误的判断。"),
            
            ("皇后", ["丰饶", "母性", "创造力", "nourishing能量", "感性"], 
             "代表丰收、富足和创造力。象征着母性的nourishing能量，无论是创造生命、艺术还是项目，都能茁壮成长。在爱情中，表示充满爱与关怀的关系。在生活中，是享受感官愉悦和物质舒适的时刻。", 
             "代表创造力受阻、过度依赖或情感上的窒息。可能表示在关系中过度付出而失去自我，或在物质上过于放纵。需要关注自我照顾，并为自己的创造力找到健康的出口。"),
            
            ("皇帝", ["权威", "结构", "控制", "领导力", "稳定"], 
             "代表权威、秩序和领导力。象征着通过建立规则和结构来实现稳定和成功。在事业上，表示强大的领导能力和组织能力。在个人生活中，需要自律和责任感来达成目标。", 
             "代表专制、过度控制或缺乏弹性。可能因为过于僵化而压抑了他人的创造力，或在关系中表现出强烈的控制欲。需要学会放手，并以更灵活的方式行使权力。"),
            
            ("教皇", ["传统", "信仰", "精神指导", "学习", "归属感"], 
             "代表传统、信仰和精神指导。鼓励遵循既定的规则和传统智慧，向有经验的导师学习。在团体中能找到归属感。在人生道路上，是寻求精神慰藉和道德指引的时刻。", 
             "代表挑战传统、思想僵化或教条主义。可能因为墨守成规而拒绝新的可能性，或盲目遵从权威而失去独立思考。需要质疑既有信念，找到适合自己的真理。"),
            
            ("恋人", ["选择", "关系", "和谐", "结合", "价值观"], 
             "代表重要的选择，尤其是在关系和价值观方面。象征着和谐的结合与深层的情感连接。在爱情中，预示着一段重要的关系或承诺。在决策时，需要遵循内心的价值观，做出忠于自己的选择。", 
             "代表关系冲突、错误的决定或价值观不合。可能在关系中感到不和谐，或在选择面前犹豫不决。需要重新审视自己的价值观，并与伴侣进行坦诚的沟通。"),
            
            ("战车", ["意志力", "胜利", "控制", "决心", "行动"], 
             "代表凭借强大的意志力和决心取得胜利。象征着通过自律和专注克服障碍，朝着目标奋勇前进。在事业上，是采取果断行动、争取成功的时刻。在挑战面前，需要保持自信和控制力。", 
             "代表失控、缺乏方向或行动力不足。可能因为目标不明确而分散了精力，或在前进的道路上遇到了无法控制的障碍。需要重新聚焦目标，并整合内在的冲突力量。"),
            
            ("力量", ["内在力量", "勇气", "耐心", "慈悲", "整合"], 
             "代表内在的勇气和温和的力量。不是通过外在的强迫，而是通过内心的慈悲和耐心来驯服野性的本能。在困境中，展现出坚韧不拔的毅力。在人际关系中，以柔克刚是解决问题的关键。", 
             "代表软弱、缺乏自信或被内在的恐惧所控制。可能因为怀疑自己的能力而不敢行动，或在压力下表现出不必要的攻击性。需要重新连接内在的力量，并以更温和的方式面对挑战。"),
            
            ("隐者", ["内省", "独处", "寻求智慧", "指导", "灵性探索"], 
             "代表向内探索、寻求智慧的时期。鼓励暂时远离尘嚣，通过独处和内省来寻找答案。在人生旅途中，是一位内在的导师在指引方向。在决策前，需要花时间进行深入的思考。", 
             "代表孤立、与社会脱节或拒绝他人的帮助。可能因为过度沉浸在自己的世界里而感到孤独，或因为固执而拒绝有益的建议。需要找到独处与社交之间的平衡。"),
            
            ("命运之轮", ["变化", "命运", "转折点", "机会", "循环"], 
             "代表生命中不可避免的变化和转折点。象征着运气的起伏和宇宙的循环法则。当时来运转时，要抓住机遇。当时运不济时，要保持耐心，相信一切终将过去。这是一个顺势而为的时刻。", 
             "代表厄运、抗拒改变或失控的局面。可能感觉到被命运捉弄，或因为抗拒生命中的自然变化而感到痛苦。需要学会接受无法控制的事情，并从中寻找成长的机会。"),
            
            ("正义", ["公正", "平衡", "真理", "因果", "责任"], 
             "代表公正、平衡和因果法则。强调需要为自己的行为承担责任，并做出符合真理和道德的决定。在法律事务或合约中，预示着一个公平的结果。在个人生活中，是审视自己行为、寻求内心平衡的时刻。", 
             "代表不公正、偏见或逃避责任。可能在某件事情上受到了不公平的对待，或自己做出了带有偏见的判断。需要面对真相，并为自己的错误承担后果。"),
            
            ("倒吊人", ["牺牲", "等待", "新视角", "顺从", "放下"], 
             "代表通过暂时的牺牲或等待来获得新的视角。鼓励放下执念，顺从于当下的安排。这是一个暂停行动、向内看的时期。通过转换角度，之前无法解决的问题可能会豁然开朗。", 
             "代表无意义的牺牲、停滞不前或拖延。可能因为害怕改变而陷入僵局，或做出了不必要的牺牲却没有换来任何回报。需要评估当前的处境，并采取行动来打破停滞。"),
            
            ("死神", ["结束", "转变", "重生", "放下过去", "变革"], 
             "代表一个周期的结束和另一个周期的开始。虽然可能伴随着痛苦告别，但这是通往重生和成长的必经之路。需要放下不再服务于你的人、事、物，为新的可能性腾出空间。", 
             "代表抗拒改变、停滞不前或无法从过去中走出来。因为害怕结束而紧抓不放，反而阻碍了新的成长。需要鼓起勇气，接受生命中必要的终结，并相信未来的可能性。"),
            
            ("节制", ["平衡", "耐心", "调和", "整合", "中庸"], 
             "代表平衡、和谐与耐心。鼓励在生活的各个方面寻找中庸之道，将对立的力量调和成一个和谐的整体。在人际关系中，是有效沟通和相互理解的象征。在个人发展中，需要耐心和稳定的步伐。", 
             "代表失衡、极端或缺乏耐心。可能在生活的某个方面过度放纵，或因为急于求成而导致混乱。需要重新找到内心的平静，并以更温和、更有耐心的方式来处理问题。"),
            
            ("恶魔", ["束缚", "诱惑", "物质主义", "成瘾", "阴影面"], 
             "代表被物质欲望、不良习惯或负面思想所束缚。象征着我们内心的阴影面和未被疗愈的创伤。需要勇敢地面对自己的欲望和恐惧，才能从中解放出来。也可能表示一段充满激情但可能不健康的关系。", 
             "代表摆脱束缚、打破成瘾或获得精神上的觉醒。象征着意识到自己所处的困境，并开始采取行动来重获自由。这是一个重新掌控自己人生的有力时机。"),
            
            ("塔", ["突变", "灾难", "启示", "解放", "颠覆"], 
             "代表突如其来的、颠覆性的变化。长期以来建立的虚假信念或结构可能会瞬间崩塌，虽然过程痛苦，但这会带来真相的启示和最终的解放。这是一个被迫面对现实、重建基础的时刻。", 
             "代表避免必要的改变、害怕灾难或拖延危机。因为害怕面对真相而维持着一个不稳定的结构，但这只会让最终的崩溃更具破坏性。需要主动迎接改变，而不是被动地等待灾难降临。"),
            
            ("星星", ["希望", "灵感", "治愈", "平静", "精神指引"], 
             "代表在黑暗中重燃希望，获得灵感和治愈。在经历了混乱之后，内心重归平静。这是一个充满信念和乐观精神的时期，宇宙正在为你提供精神上的指引。对未来充满信心。", 
             "代表绝望、失去信念或与灵感脱节。可能因为之前的困境而感到心灰意冷，看不到未来的方向。需要重新找回内心的希望之光，并相信自己有能力克服困难。"),
            
            ("月亮", ["幻觉", "恐惧", "潜意识", "直觉", "迷惑"], 
             "代表深入潜意识的领域，面对内心的恐惧和幻觉。情况可能并不像表面看起来那样清晰，需要依赖直觉来导航。这是一个充满不确定性和迷惑的时期，但也是探索内心深处秘密的机会。", 
             "代表克服恐惧、看清真相或走出迷惑。当理智的光芒照进潜意识的黑暗，之前模糊不清的事情会变得明朗。这是一个从焦虑和不安中解脱出来，重获内心清晰的时刻。"),
            
            ("太阳", ["成功", "喜悦", "活力", "清晰", "乐观"], 
             "代表成功、喜悦和生命的活力。所有的疑虑和困惑都已消散，前方的道路清晰而光明。这是一个充满自信和乐观精神的时期，尽情享受努力带来的成果和使用中的乐趣吧。", 
             "代表暂时的挫折、缺乏热情或过度自信。虽然目标最终可以达成，但可能会遇到一些延迟。也可能因为过于乐观而忽视了细节。需要保持谦逊，并重新点燃对生活的热情。"),
            
            ("审判", ["重生", "觉醒", "清算", "宽恕", "召唤"], 
             "代表一个重要的觉醒时刻，对过去进行清算和反思，并做出最终的评判。这是一个获得宽恕、迎接重生的机会。你正在被召唤去实现一个更高的目标，开启人生的新篇章。", 
             "代表自我怀疑、逃避评判或拒绝成长的机会。可能因为害怕面对过去的错误而陷入内疚和悔恨之中。需要学会宽恕自己和他人，并勇敢地回应内在的成长召唤。"),
            
            ("世界", ["完成", "整合", "成就", "圆满", "旅行"], 
             "代表一个周期的圆满完成和目标的达成。所有的努力都得到了回报，你已经将生命的各个方面成功地整合在一起。这是一个庆祝成就、享受和谐与满足的时刻。也可能预示着长途旅行或走向世界。 ", 
             "代表未完成的事业、缺乏闭环或停滞不前。虽然离成功仅一步之遥，但因为某些原因而无法达到最终的圆满。需要审视是哪个环节出了问题，并努力完成这最后的旅程。")
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
        minor_arcana_meanings = {
            Suit.WANDS: {
                "suit_name": "权杖", "suit_desc": "火元素，代表激情、创造力、行动和意志力",
                "cards": {
                    1: (["新起点", "灵感", "行动力"], "新的激情或项目开始，充满创造力的火花。", "计划延迟，缺乏动力，方向不明确。"),
                    2: (["计划", "决策", "个人力量"], "站在十字路口，需要规划未来，评估选择。", "害怕未知，缺乏长远计划，优柔寡断。"),
                    3: (["扩展", "远见", "领导力"], "初步成功，是时候将眼光放得更远，寻求合作。", "计划受阻，缺乏远见，合作出现问题。"),
                    4: (["庆祝", "和谐", "稳定"], "庆祝阶段性的成功，享受家庭的和谐与稳定。", "关系不稳定，家庭内部有矛盾，庆祝被推迟。"),
                    5: (["竞争", "冲突", "分歧"], "良性的竞争或冲突，不同意见的碰撞。", "激烈的冲突，混乱，为避免冲突而压抑自己。"),
                    6: (["胜利", "认可", "成功"], "取得公开的胜利和认可，享受成功的喜悦。", "成功延迟，缺乏认可，骄傲自大导致失败。"),
                    7: (["挑战", "勇气", "坚守立场"], "面对挑战，需要鼓起勇气，捍卫自己的立场。", "不堪重负，寡不敌众，放弃自己的立场。"),
                    8: (["快速行动", "消息", "旅行"], "事情进展迅速，可能收到重要消息或有旅行机会。", "行动受阻，延迟，错过重要消息。"),
                    9: (["坚韧", "防御", "毅力"], "经历了战斗后的疲惫，但仍需保持警惕和毅力。", "固执己见，偏执，无法放下过去的伤痛。"),
                    10: (["负担", "责任", "压力"], "承担了过多的责任和负担，感到压力巨大。", "不堪重负，放弃责任，被压力压垮。"),
                    "侍从": (["热情", "探索", "信使"], "充满好奇心和热情，渴望探索新领域，带来新消息。", "缺乏方向，热情无法持续，带来坏消息。"),
                    "骑士": (["行动力", "热情", "冲动"], "充满活力，迅速采取行动，但可能有些冲动。", "鲁莽行事，冲动导致错误，精力耗尽。"),
                    "王后": (["自信", "魅力", "创造力"], "充满自信和魅力的领导者，能激励他人。", "嫉妒，报复心强，创造力被压抑。"),
                    "国王": (["领导力", "远见", "权威"], "有远见的、成熟的领导者，掌控全局。", "专制，滥用权力，缺乏远见。")
                }
            },
            Suit.CUPS: {
                "suit_name": "圣杯", "suit_desc": "水元素，代表情感、关系、直觉和创造力",
                "cards": {
                    1: (["新恋情", "情感流动", "创造力"], "新的情感开始，爱与创造力的涌现。", "情感压抑，关系空虚，创造力受阻。"),
                    2: (["结合", "伙伴关系", "吸引力"], "和谐的伙伴关系，灵魂的连接，相互吸引。", "关系失衡，分手，沟通不畅。"),
                    3: (["庆祝", "友谊", "团体"], "与朋友们一起庆祝，享受社交的乐趣。", "过度放纵，友谊破裂，孤独。"),
                    4: (["冷漠", "沉思", "错失机会"], "对现状感到不满和冷漠，错过了新的机会。", "走出冷漠，接受新的机会，重新燃起热情。"),
                    5: (["失落", "悲伤", "失望"], "为失去而悲伤，但仍有希望存在。", "无法走出悲伤，沉溺于过去，看不到希望。"),
                    6: (["怀旧", "童年", "纯真"], "美好的回忆，与过去的人重逢，重拾纯真。", "沉溺于过去，无法成长，童年创伤。"),
                    7: (["幻想", "选择", "白日梦"], "面临多种选择，但很多是不切实际的幻想。", "从幻想中清醒，做出明确的选择，付诸行动。"),
                    8: (["离开", "追寻", "放弃"], "为了追寻更深层的意义而离开熟悉的环境。", "害怕改变，停滞不前，不知道自己想要什么。"),
                    9: (["满足", "愿望成真", "舒适"], "情感和物质上的满足，愿望得以实现。", "自满，贪婪，物质主义。"),
                    10: (["和谐", "幸福家庭", "情感圆满"], "家庭幸福，情感上的终极满足与和谐。", "家庭不和，关系破裂，无法实现情感满足。"),
                    "侍从": (["直觉", "信息", "创造力"], "倾听直觉，收到情感方面的信息，富有创造力。", "情感不成熟，逃避现实，创造力被压抑。"),
                    "骑士": (["浪漫", "魅力", "理想主义"], "浪漫的追求者，富有魅力，但可能过于理想化。", "情感操控，善变，不切实际的幻想。"),
                    "王后": (["同情心", "直觉", "滋养"], "富有同情心和直觉力，能提供情感支持。", "情绪化，过度敏感，情感勒索。"),
                    "国王": (["情感成熟", "控制", "智慧"], "情感成熟且自控的领导者，充满智慧和同情心。", "情感操控，喜怒无常，压抑情感。")
                }
            },
            Suit.SWORDS: {
                "suit_name": "宝剑", "suit_desc": "风元素，代表思想、沟通、冲突和挑战",
                "cards": {
                    1: (["清晰", "突破", "真理"], "思想上的突破，获得清晰的认知，看到真相。", "混乱，困惑，错误的决定。"),
                    2: (["僵局", "选择", "逃避"], "处于两难境地，需要做出决定但选择逃避。", "做出艰难的决定，看清真相，打破僵局。"),
                    3: (["心碎", "悲伤", "分离"], "经历痛苦的分离或背叛，感到心碎。", "从悲伤中恢复，原谅，接受现实。"),
                    4: (["休息", "恢复", "沉思"], "需要从冲突和压力中暂时退出，进行休息和恢复。", "精疲力竭，停滞不前，拒绝休息。"),
                    5: (["冲突", "失败", "不光彩的胜利"], "冲突后的失败感，或以不光彩的方式取胜。", "和解，放下争斗，寻求双赢。"),
                    6: (["过渡", "旅行", "解脱"], "从困境中走出，进入一个更平静的时期，可能是字面上的旅行。", "无法摆脱过去，过渡期遇到困难，计划受阻。"),
                    7: (["欺骗", "策略", "逃避"], "使用策略或欺骗来达到目的，可能在逃避责任。", "面对现实，诚实，放弃无效的策略。"),
                    8: (["束缚", "限制", "无助感"], "感觉被困住，受到限制，但这种束缚多是自我造成的。", "打破束缚，重获自由，意识到自己的力量。"),
                    9: (["焦虑", "恐惧", "噩梦"], "被焦虑、恐惧和担忧所困扰，夜不能寐。", "面对恐惧，寻求帮助，从焦虑中解脱。"),
                    10: (["终结", "失败", "背叛"], "痛苦的终结，彻底的失败，被背叛的感觉。", "接受失败，从谷底反弹，迎来新的开始。"),
                    "侍从": (["好奇", "沟通", "新思想"], "充满好奇，渴望学习和沟通，带来新思想。", "散播谣言，说话不经思考，缺乏深度。"),
                    "骑士": (["果断", "野心", "行动迅速"], "目标明确，行动迅速，充满野心，但可能缺乏同情心。", "鲁莽，攻击性强，不择手段。"),
                    "王后": (["智慧", "独立", "清晰"], "诚实、独立、智慧的女性，思路清晰，不感情用事。", "刻薄，孤立，滥用智慧。"),
                    "国王": (["权威", "智慧", "公正"], "智慧、公正、有权威的领导者，善于沟通和决策。", "专制，冷酷无情，滥用权力。")
                }
            },
            Suit.PENTACLES: {
                "suit_name": "星币", "suit_desc": "土元素，代表物质、金钱、工作和现实",
                "cards": {
                    1: (["机会", "显化", "繁荣"], "新的物质机会，是实现财务目标的好时机。", "错失机会，财务计划不周，投资失败。"),
                    2: (["平衡", "适应性", "变化"], "在变化中保持平衡，灵活地处理多项任务。", "财务不稳定，无法兼顾，生活失衡。"),
                    3: (["团队合作", "技能", "品质"], "通过团队合作和精湛的技能获得成功。", "合作不畅，工作质量差，缺乏团队精神。"),
                    4: (["占有", "稳定", "保守"], "追求物质上的稳定和安全，但可能过于保守和吝啬。", "财务损失，慷慨，放下对物质的执着。"),
                    5: (["贫困", "逆境", "孤立"], "经历物质上的困难，感到被孤立和遗弃。", "走出困境，接受帮助，找到希望。"),
                    6: (["慷慨", "慈善", "分享"], "慷慨地给予或接受帮助，实现财务上的平衡。", "债务，吝啬，不平等的给予和接受。"),
                    7: (["耐心", "评估", "回报"], "耐心等待投资的回报，评估目前的进展。", "不耐烦，急于求成，对结果感到失望。"),
                    8: (["技能", "专注", "精通"], "通过努力工作和专注来提升技能，追求精通。", "工作马虎，缺乏野心，半途而废。"),
                    9: (["富足", "独立", "享受成果"], "享受辛勤工作带来的物质富足和独立。", "财务依赖，过度消费，空虚。"),
                    10: (["财富", "传承", "家庭"], "长期的物质成功和家庭财富的传承。", "家庭财务纠纷，财富损失，不稳定。"),
                    "侍从": (["学习", "机会", "勤奋"], "渴望学习新技能，带来实际的机会，勤奋努力。", "懒惰，错失机会，缺乏实践。"),
                    "骑士": (["可靠", "耐心", "努力工作"], "可靠、有耐心、努力工作的人，脚踏实地。", "固执，停滞不前，过于追求物质。"),
                    "王后": (["滋养", "务实", "慷慨"], "务实、慷慨、懂得享受生活的女性，能提供物质支持。", "物质主义，嫉妒，过度关注外表。"),
                    "国王": (["富裕", "成功", "可靠"], "成功、可靠、慷慨的领导者，善于创造和维护财富。", "贪婪，腐败，过于保守。")
                }
            }
        }

        court_cards = ["侍从", "骑士", "王后", "国王"]
        
        for suit, suit_data in minor_arcana_meanings.items():
            suit_name = suit_data["suit_name"]
            suit_desc = suit_data["suit_desc"]
            
            # 数字牌 1-10
            for num in range(1, 11):
                keywords, upright, reversed_mean = suit_data["cards"][num]
                cards.append(TarotCard(
                    name=f"{suit_name}{num}",
                    suit=suit,
                    number=num,
                    keywords=keywords,
                    upright_meaning=upright,
                    reversed_meaning=reversed_mean,
                    description=f"{suit_desc}的数字牌"
                ))
            
            # 宫廷牌
            for court in court_cards:
                keywords, upright, reversed_mean = suit_data["cards"][court]
                cards.append(TarotCard(
                    name=f"{suit_name}{court}",
                    suit=suit,
                    number=None, # 宫廷牌没有数字
                    keywords=keywords,
                    upright_meaning=upright,
                    reversed_meaning=reversed_mean,
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
        4. 爱情关系牌阵 - 深入了解感情状况和相关方向
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
    
    def _get_specialized_prompt_suffix(self, question: str) -> str:
        """根据问题类型添加专门的prompt后缀"""
        question_lower = question.lower()
        
        if any(keyword in question_lower for keyword in ['爱情', '感情', '恋爱', '婚姻', '关系']):
            return """
## 💕 爱情关系专项指导
请特别关注以下方面：
- 双方的情感状态和需求
- 关系发展的自然节奏
- 沟通和理解的重要性
- 个人成长对关系的影响
- 如何建立更深层的连接
"""
        
        elif any(keyword in question_lower for keyword in ['工作', '事业', '职业', '升职', '跳槽']):
            return """
## 💼 的事业专项指导
请特别关注以下方面：
- 当前职业状态的评估
- 技能发展和学习方向
- 人际关系和团队合作
- 机遇识别和风险管控
- 长期职业规划建议
"""
        
        elif any(keyword in question_lower for keyword in ['决定', '选择', '决策']):
            return """
## ⚖️ 决策分析专项指导
请特别关注以下方面：
- 各选项的优劣势分析
- 决策的时机和条件
- 潜在的风险和机遇
- 内心真实的渴望
- 决策后的行动策略
"""
        
        return ""

    def _build_prompt(self, reading: TarotReading) -> str:
        """构建增强版LLM提示词"""
        cards_info = []
        # 获取牌阵的位置描述
        spread_positions = self.get_spread_positions(reading.spread_type)

        for i, card in enumerate(reading.cards):
            position = "逆位 🔄" if reading.reversed_cards[i] else "正位 ⬆️"
            # 使用牌阵的预设位置名称，如果超出则使用通用名称
            position_name = spread_positions[i] if i < len(spread_positions) else f"位置{i+1}"
            
            element_info = f"({card.suit.value}" + (f", {card.number}号牌" if card.number is not None else ", 宫廷牌") + ")"
            keywords = ", ".join(card.keywords)
            
            cards_info.append(f"""
**{position_name}**: {card.name} {element_info}
- **状态**: {position}
- **关键词**: {keywords}
- **正位含义**: {card.upright_meaning}
- **逆位含义**: {card.reversed_meaning}
""")
        
        specialized_suffix = self._get_specialized_prompt_suffix(reading.question)

        prompt = f"""你是一位拥有30年经验的专业塔罗牌占卜师，精通韦特塔罗牌系统和各种牌阵解读。请为以下塔罗牌占卜提供深入、准确、富有同情心和建设性的解读。

## 📋 占卜信息
**问题**: {reading.question if reading.question else '寻求一般性的人生指导'}
**牌阵**: {reading.spread_type}
**牌阵说明**: {reading.spread_description}
**占卜时间**: {reading.timestamp.strftime('%Y年%m月%d日 %H:%M:%S')}

## 🃏 抽取的牌面
{''.join(cards_info)}

## 📖 解读要求
请按照以下结构提供专业、详细的解读：

### 1. 🎯 整体能量概览 (Overall Energy)
- **核心信息**: 总结这次占卜传达的最核心的信息和主题。
- **能量流向**: 分析牌面的整体能量是积极的、挑战的还是复杂的？主导的元素能量（权杖/火、圣杯/水、宝剑/风、星币/土）是什么，它揭示了什么？

### 2. 🔍 逐张牌面解析 (Card-by-Card Analysis)
- 按照牌阵中每个位置的特定含义，深入解读对应的牌。
- 结合牌的正位/逆位状态，解释它在该位置上的具体影响。
- 将牌意与问卜者的问题紧密联系起来。

### 3. 🔗 牌面间的互动关系 (Interconnections)
- 分析牌与牌之间是如何相互影响的，它们共同讲述了一个怎样的故事？
- 识别出关键的牌面组合（例如，连续出现的大阿卡纳，或某个元素占主导）。
- 指出能量的流动、冲突或加强之处。

### 4. 💡 核心洞察与行动建议 (Key Insights & Actionable Advice)
- **核心洞察**: 提炼出最重要的洞察，帮助问卜者理解当前局面的本质。
- **行动建议**: 提供清晰、具体、可行的行动步骤。应该做什么？避免什么？
- **心态调整**: 建议问卜者应该采取何种心态来面对当前状况。

### 5. 🌟 总结与精神指引 (Summary & Spiritual Guidance)
- **总结**: 用几句鼓励人心的话总结这次占卜的最终指引。
- **精神指引**: 从更高的精神层面，提炼出这次经历对问卜者个人成长的意义。
{specialized_suffix}
## 📝 解读风格要求
- **语调**: 温和、智慧、富有同情心且充满鼓励。
- **视角**: 避免宿命论，强调个人自由意志和选择的力量。将塔罗牌视为一面镜子和一份指引，而非绝对的预言。
- **重点**: 聚焦于提供建设性的解决方案和积极的成长路径。

请开始您的专业解读："""
        
        return prompt

    def get_spread_positions(self, spread_type: str) -> list[str]:
        """获取指定牌阵的位置名称"""
        # 这个方法需要访问SpreadRecommender中的牌阵定义
        # 为了解耦，我们在这里硬编码一个映射，理想情况下可以重构
        spreads = {
            "single_card": ["当前指引"],
            "three_card_time": ["过去", "现在", "未来"],
            "three_card_situation": ["情况", "行动", "结果"],
            "love_relationship": ["你的感受", "对方的感受", "关系现状", "挑战", "未来发展"],
            "career_guidance": ["当前状况", "优势", "挑战", "机会", "建议行动", "未来前景"],
            "decision_making": ["当前情况", "选择A", "选择A结果", "选择B", "选择B结果", "外在影响", "最佳建议"],
            "celtic_cross": ["当前状况", "挑战", "远因", "近因", "可能结果", "近期发展", "你的态度", "外在影响", "内心期望", "最终结果"],
            "year_forecast": [f"{i+1}月" for i in range(12)]
        }
        return spreads.get(spread_type, [])

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

