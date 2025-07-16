from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from tarot_reader import TarotApp, TarotDeck, SpreadRecommender, LLMTarotInterpreter, ResultSaver, TarotReading

app = Flask(__name__)
app.secret_key = 'tarot_secret_key_2024'

# 添加 CORS 支持
CORS(app, origins=["http://localhost:5173"])  # Vue 3 开发服务器默认端口

# 初始化塔罗牌组件
tarot_deck = TarotDeck()
recommender = SpreadRecommender()
interpreter = LLMTarotInterpreter()
saver = ResultSaver()
# 添加TarotApp实例
tarot_app = TarotApp()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/recommend_spreads', methods=['POST'])
def recommend_spreads():
    """获取牌阵推荐"""
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': '请输入问题'}), 400
        
        # 获取推荐牌阵
        recommended_keys = recommender.get_recommendations(question)
        
        # 返回推荐牌阵的详细信息
        recommendations = []
        for key in recommended_keys:
            spread = recommender.spreads[key]
            recommendations.append({
                'key': key,
                'name': spread['name'],
                'cards': spread['cards'],
                'description': spread['description'],
                'positions': spread.get('positions', [])
            })
        
        return jsonify({
            'recommendations': recommendations,
            'all_spreads': {
                key: {
                    'name': spread['name'],
                    'cards': spread['cards'],
                    'description': spread['description'],
                    'positions': spread.get('positions', [])
                }
                for key, spread in recommender.spreads.items()
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 修改获取所有牌阵的API
@app.route('/api/get_all_spreads', methods=['GET'])
def get_all_spreads():
    try:
        spreads = recommender.spreads  # 使用recommender而不是tarot_reader
        return jsonify({
            'spreads': spreads
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 修改抽牌API以支持模式参数
@app.route('/api/draw_cards', methods=['POST'])
def draw_cards():
    try:
        data = request.get_json()
        question = data.get('question', '')
        spread_key = data.get('spread_key')
        mode = data.get('mode', 'guided')
        
        if not spread_key:
            return jsonify({'error': '请选择牌阵'}), 400
            
        # 专家模式允许空问题
        if mode == 'guided' and not question:
            return jsonify({'error': '请输入问题'}), 400
        
        # 获取牌阵信息
        if spread_key not in recommender.spreads:
            return jsonify({'error': '无效的牌阵'}), 400
            
        spread = recommender.spreads[spread_key]
        
        # 洗牌并抽牌
        tarot_deck.shuffle()
        cards = tarot_deck.draw_cards(spread['cards'])
        
        # 创建占卜结果
        reading = TarotReading(
            cards=cards,
            spread_type=spread['name'],
            spread_description=spread['description'],
            question=question if question else '一般性指导'
        )
        
        # 获取牌阵位置信息
        positions = spread.get('positions', [])
        
        # 转换为字典格式返回
        result = {
            'cards': [{
                'name': card.name,
                'suit': card.suit.value,
                'number': card.number,
                'keywords': card.keywords,
                'upright_meaning': card.upright_meaning,
                'reversed_meaning': card.reversed_meaning,
                'description': card.description,
                'is_reversed': reading.reversed_cards[i],
                'position': positions[i] if i < len(positions) else f'位置{i+1}'  # 添加位置信息
            } for i, card in enumerate(cards)],
            'spread': {
                'key': spread_key,
                'name': spread['name'],
                'description': spread['description'],
                'positions': spread.get('positions', [])
            },
            'question': question if question else '一般性指导',
            'timestamp': reading.timestamp.isoformat()
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/interpret', methods=['POST'])
def interpret_reading():
    """AI解读"""
    try:
        data = request.get_json()
        
        # 重建TarotReading对象
        cards_data = data.get('cards', [])
        spread_data = data.get('spread', {})
        question = data.get('question', '')
        
        # 这里需要重建cards对象，简化处理
        from tarot_reader import TarotCard, Suit
        
        cards = []
        reversed_cards = []
        
        for card_data in cards_data:
            # 根据suit字符串找到对应的Suit枚举
            suit_map = {
                '大阿卡纳': Suit.MAJOR_ARCANA,
                '权杖': Suit.WANDS,
                '圣杯': Suit.CUPS,
                '宝剑': Suit.SWORDS,
                '星币': Suit.PENTACLES
            }
            
            suit = suit_map.get(card_data['suit'], Suit.MAJOR_ARCANA)
            
            card = TarotCard(
                name=card_data['name'],
                suit=suit,
                number=card_data.get('number'),
                keywords=card_data.get('keywords', []),
                upright_meaning=card_data.get('upright_meaning', ''),
                reversed_meaning=card_data.get('reversed_meaning', ''),
                description=card_data.get('description', '')
            )
            
            cards.append(card)
            reversed_cards.append(card_data.get('is_reversed', False))
        
        # 创建TarotReading对象
        reading = TarotReading(
            cards=cards,
            spread_type=spread_data.get('name', ''),
            spread_description=spread_data.get('description', ''),
            question=question
        )
        reading.reversed_cards = reversed_cards
        
        # 获取AI解读
        interpretation = interpreter.interpret_reading(reading)
        
        # 注意：这里仍然保存结果到本地，但不提供历史记录查看功能
        filepath = saver.save_reading(reading, interpretation)
        
        return jsonify({
            'interpretation': interpretation,
            'saved_file': filepath
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    """下载占卜结果文件"""
    try:
        return send_from_directory('answers', filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': '文件不存在'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)