class TarotApp {
    constructor() {
        this.currentReading = null;
        this.currentMode = null;
        this.init();
    }

    init() {
        this.bindEvents();
    }

    bindEvents() {
        // 模式选择事件监听器
        document.getElementById('guided-mode').addEventListener('click', () => {
            this.selectMode('guided');
        });
        
        document.getElementById('expert-mode').addEventListener('click', () => {
            this.selectMode('expert');
        });
        
        // 返回模式选择
        document.getElementById('back-to-mode-selection').addEventListener('click', () => {
            this.showModeSelection();
        });
        
        // 显示所有牌阵（专家模式）
        document.getElementById('show-all-spreads').addEventListener('click', () => {
            this.showAllSpreads();
        });

        // 获取推荐牌阵
        document.getElementById('get-recommendations').addEventListener('click', () => {
            this.getRecommendations();
        });

        // 返回问题输入
        document.getElementById('back-to-question').addEventListener('click', () => {
            this.showSection('question-section');
        });

        // 获取AI解读
        document.getElementById('get-interpretation').addEventListener('click', () => {
            this.getInterpretation();
        });

        // 新的占卜
        document.getElementById('new-reading').addEventListener('click', () => {
            this.newReading();
        });

        document.getElementById('new-reading-2').addEventListener('click', () => {
            this.newReading();
        });

        // 导航按钮
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const section = e.currentTarget.dataset.section;
                this.showSection(section);
                this.updateNavigation(e.currentTarget);
            });
        });

        // 回车键提交问题
        document.getElementById('question-input').addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.getRecommendations();
            }
        });
    }

    // 模式选择方法
    selectMode(mode) {
        // 隐藏模式选择
        document.querySelector('.mode-selection').style.display = 'none';
        
        if (mode === 'guided') {
            // 显示引导模式输入
            document.getElementById('guided-input').style.display = 'block';
            document.getElementById('expert-input').style.display = 'none';
        } else {
            // 显示专家模式输入
            document.getElementById('guided-input').style.display = 'none';
            document.getElementById('expert-input').style.display = 'block';
        }
        
        // 显示返回按钮
        document.getElementById('back-to-mode').style.display = 'block';
        
        this.currentMode = mode;
    }

    showModeSelection() {
        // 显示模式选择
        document.querySelector('.mode-selection').style.display = 'flex';
        
        // 隐藏输入区域
        document.getElementById('guided-input').style.display = 'none';
        document.getElementById('expert-input').style.display = 'none';
        document.getElementById('back-to-mode').style.display = 'none';
        
        this.currentMode = null;
    }

    async showAllSpreads() {
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/get_all_spreads');
            const data = await response.json();
            
            if (response.ok) {
                this.displayAllSpreads(data.spreads);
                this.showSection('spread-section');
            } else {
                this.showMessage(data.error || '获取牌阵失败', 'error');
            }
        } catch (error) {
            this.showMessage('网络错误，请重试', 'error');
            console.error('Error:', error);
        } finally {
            this.showLoading(false);
        }
    }

    displayAllSpreads(spreads) {
        const recommendedContainer = document.getElementById('recommended-spreads');
        const allContainer = document.getElementById('all-spreads');
        
        // 隐藏推荐区域标题
        recommendedContainer.parentElement.querySelector('h2').style.display = 'none';
        recommendedContainer.innerHTML = '';
        
        // 显示所有牌阵
        allContainer.parentElement.querySelector('h3').textContent = '选择牌阵';
        allContainer.innerHTML = '';
        Object.entries(spreads).forEach(([key, spread]) => {
            const spreadElement = this.createSpreadElement({...spread, key}, false);
            allContainer.appendChild(spreadElement);
        });
    }

    // 获取推荐牌阵
    async getRecommendations() {
        const question = document.getElementById('question-input').value.trim();
        
        if (!question) {
            this.showMessage('请输入您的问题', 'error');
            return;
        }

        this.showLoading(true);

        try {
            const response = await fetch('/api/recommend_spreads', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question })
            });

            const data = await response.json();

            if (response.ok) {
                this.displaySpreads(data.recommendations, data.all_spreads);
                this.showSection('spread-section');
            } else {
                this.showMessage(data.error || '获取推荐失败', 'error');
            }
        } catch (error) {
            this.showMessage('网络错误，请重试', 'error');
            console.error('Error:', error);
        } finally {
            this.showLoading(false);
        }
    }

    displaySpreads(recommendations, allSpreads) {
        const recommendedContainer = document.getElementById('recommended-spreads');
        const allContainer = document.getElementById('all-spreads');
        
        // 显示推荐牌阵
        recommendedContainer.innerHTML = '';
        recommendations.forEach(spread => {
            const spreadElement = this.createSpreadElement(spread, true);
            recommendedContainer.appendChild(spreadElement);
        });

        // 显示所有牌阵
        allContainer.innerHTML = '';
        Object.entries(allSpreads).forEach(([key, spread]) => {
            const isRecommended = recommendations.some(r => r.key === key);
            if (!isRecommended) {
                const spreadElement = this.createSpreadElement({...spread, key}, false);
                allContainer.appendChild(spreadElement);
            }
        });
    }

    createSpreadElement(spread, isRecommended) {
        const div = document.createElement('div');
        div.className = `spread-item ${isRecommended ? 'recommended' : ''}`;
        div.innerHTML = `
            <div class="spread-name">${spread.name}</div>
            <div class="spread-info">${spread.cards} 张牌</div>
            <div class="spread-description">${spread.description}</div>
        `;
        
        div.addEventListener('click', () => {
            this.selectSpread(spread.key);
        });
        
        return div;
    }

    // 修改createTarotCard方法
    createTarotCard(card, index, spreadType) {
        const cardContainer = document.createElement('div');
        cardContainer.className = 'tarot-card-container';
        
        const tarotCard = document.createElement('div');
        tarotCard.className = `tarot-card ${card.is_reversed ? 'reversed' : ''}`;
        
        // 卡牌正面
        const cardFront = document.createElement('div');
        cardFront.className = 'card-face card-front';
        
        // 添加牌面图像（带错误处理）
        const cardImage = this.getCardImage(card);
        if (cardImage) {
            const img = document.createElement('img');
            img.src = cardImage;
            img.className = 'card-image';
            img.alt = card.name;
            
            // 添加图片加载错误处理
            img.onerror = () => {
                img.style.display = 'none';
                // 如果图片加载失败，显示卡牌名称作为替代
                const fallback = document.createElement('div');
                fallback.className = 'card-image-fallback';
                fallback.style.cssText = `
                    width: 100%;
                    height: 75%;
                    background: linear-gradient(135deg, #2d1b69, #11998e);
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: #ffd700;
                    font-weight: bold;
                    text-align: center;
                    font-size: 0.7rem;
                    border: 2px solid rgba(255, 215, 0, 0.3);
                    margin-bottom: 6px;
                    ${card.is_reversed ? 'transform: rotateZ(180deg);' : ''}
                `;
                fallback.textContent = card.name;
                cardFront.appendChild(fallback);
            };
            
            cardFront.appendChild(img);
        }
        
        // 卡牌信息 - 修改为显示位置和名称(只有逆位才显示括号)
        const cardInfo = document.createElement('div');
        cardInfo.className = 'card-info';
        cardInfo.innerHTML = `
            <div class="card-position-label">${card.position}</div>
            <div class="card-name">${card.name}${card.is_reversed ? '（逆位）' : ''}</div>
        `;
        cardInfo.style.cssText = 'margin-top: 15px;'; // 增加间距
        cardFront.appendChild(cardInfo);
        
        // 卡牌背面
        const cardBack = document.createElement('div');
        cardBack.className = 'card-face card-back';
        
        tarotCard.appendChild(cardFront);
        tarotCard.appendChild(cardBack);
        
        // 移除正逆位指示器
        
        cardContainer.appendChild(tarotCard);
        
        // 添加点击事件显示详细信息
        tarotCard.addEventListener('click', () => {
            this.showCardDetail(card);
        });
        
        // 统一的翻牌动画
        setTimeout(() => {
            tarotCard.classList.add('flipped', 'card-reveal');
        }, index * 300);
        
        return cardContainer;
    }
    
    // 获取卡牌图像路径
    getCardImage(card) {
        return `/static/images/tarot/${card.name}.jpg`;
    }
    
    // 创建牌阵布局（统一版本）
    // 修改 displayCards 方法
    displayCards(reading) {
    // 设置牌阵标题
    document.getElementById('spread-title').innerHTML = `<i class="fas fa-cards-blank"></i> ${reading.spread.name}`;
    
    // 设置牌阵描述
    document.getElementById('spread-description').textContent = reading.spread.description;
    
    // 设置问题显示
    document.getElementById('question-display').innerHTML = `<strong>您的问题：</strong>${reading.question}`;
    
    // 创建牌阵布局（只创建卡牌，不创建信息）
    this.createSpreadLayout(reading);
    }
    
    // 修改 createSpreadLayout 方法
    createSpreadLayout(reading) {
    const container = document.getElementById('cards-container');
    container.innerHTML = '';
    
    // 直接创建牌阵布局，不再创建 spread-info
    const spreadLayout = document.createElement('div');
    spreadLayout.className = `spread-layout ${this.getSpreadClass(reading.spread.name)}`;
    
    reading.cards.forEach((card, index) => {
        const cardElement = this.createTarotCard(card, index, reading.spread.name);
        
        // 为特定牌阵添加位置类名
        const positionClass = this.getPositionClass(reading.spread.name, index);
        if (positionClass) {
            cardElement.classList.add(positionClass);
        }
        
        spreadLayout.appendChild(cardElement);
    });
    
    container.appendChild(spreadLayout);
    }

    // 获取牌阵CSS类名
    getSpreadClass(spreadName) {
        const spreadClasses = {
            '单张牌指引': 'spread-single',
            '时间三张牌': 'spread-three-time',
            '情况三张牌': 'spread-three-situation', 
            '凯尔特十字': 'spread-celtic',
            '爱情关系牌阵': 'spread-love',
            '事业指导牌阵': 'spread-career',
            '决策分析牌阵': 'spread-decision',
            '年度运势': 'spread-annual'
        };
        return spreadClasses[spreadName] || 'spread-default';
    }

    // 统一的位置类名获取方法
    getPositionClass(spreadName, index) {
        switch(spreadName) {
            case '凯尔特十字':
                return this.getCelticPosition(index);
            case '爱情关系牌阵':
                return this.getLovePosition(index);
            case '事业指导牌阵':
                return this.getCareerPosition(index);
            case '决策分析牌阵':
                return this.getDecisionPosition(index);
            case '年度运势':
                return this.getAnnualPosition(index);
            default:
                return '';
        }
    }
    
    // 事业指导牌阵位置类名
    getCareerPosition(index) {
        const positions = [
            'career-current',    // 当前状况
            'career-strength',   // 优势
            'career-challenge',  // 挑战
            'career-opportunity',// 机会
            'career-action',     // 建议行动
            'career-future'      // 未来前景
        ];
        return positions[index] || '';
    }
    
    // 决策分析牌阵位置类名
    getDecisionPosition(index) {
        const positions = [
            'decision-situation', // 当前情况
            'decision-option-a',  // 选择A
            'decision-result-a',  // 选择A结果
            'decision-option-b',  // 选择B
            'decision-result-b',  // 选择B结果
            'decision-influence', // 外在影响
            'decision-advice'     // 最佳建议
        ];
        return positions[index] || '';
    }
    
    // 年度运势位置类名
    getAnnualPosition(index) {
        const months = [
            'annual-jan', 'annual-feb', 'annual-mar', 'annual-apr',
            'annual-may', 'annual-jun', 'annual-jul', 'annual-aug', 
            'annual-sep', 'annual-oct', 'annual-nov', 'annual-dec'
        ];
        return months[index] || '';
    }
    
    // 获取凯尔特十字位置类名
    getCelticPosition(index) {
        const positions = [
            'celtic-center',
            'celtic-cross', 
            'celtic-top',
            'celtic-bottom',
            'celtic-left',
            'celtic-right',
            'celtic-staff1',
            'celtic-staff2',
            'celtic-staff3',
            'celtic-staff4'
        ];
        return positions[index] || '';
    }
    
    // 获取爱情牌阵位置类名
    getLovePosition(index) {
        const positions = [
            'love-you',
            'love-partner',
            'love-past',
            'love-present',
            'love-future',
            'love-advice'
        ];
        return positions[index] || '';
    }
    
    // 显示卡牌详细信息
    showCardDetail(card) {
        const modal = document.createElement('div');
        modal.className = 'card-detail-modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>${card.name} ${card.is_reversed ? '(逆位)' : '(正位)'}</h3>
                    <button class="close-modal">&times;</button>
                </div>
                <div class="modal-body">
                    <p><strong>花色：</strong>${card.suit}</p>
                    <p><strong>位置：</strong>${card.position}</p>
                    <p><strong>关键词：</strong>${card.keywords ? card.keywords.join(', ') : ''}</p>
                    <p><strong>含义：</strong>${card.is_reversed ? card.reversed_meaning : card.upright_meaning}</p>
                    <p><strong>描述：</strong>${card.description}</p>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // 关闭模态框
        modal.querySelector('.close-modal').addEventListener('click', () => {
            document.body.removeChild(modal);
        });
        
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                document.body.removeChild(modal);
            }
        });
    }
    
    async getInterpretation() {
        if (!this.currentReading) {
            this.showMessage('没有可解读的占卜结果', 'error');
            return;
        }

        this.showLoading(true);

        try {
            const response = await fetch('/api/interpret', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.currentReading)
            });

            const data = await response.json();

            if (response.ok) {
                this.displayInterpretation(data.interpretation);
                this.showSection('interpretation-section');
                this.showMessage('AI解读完成', 'success');
            } else {
                this.showMessage(data.error || '解读失败', 'error');
            }
        } catch (error) {
            this.showMessage('网络错误，请重试', 'error');
            console.error('Error:', error);
        } finally {
            this.showLoading(false);
        }
    }

    displayInterpretation(interpretation) {
        document.getElementById('interpretation-content').textContent = interpretation;
    }

    // 添加新方法
    selectMode(mode) {
    // 隐藏模式选择
    document.querySelector('.mode-selection').style.display = 'none';
    
    if (mode === 'guided') {
        // 显示引导模式输入
        document.getElementById('guided-input').style.display = 'block';
        document.getElementById('expert-input').style.display = 'none';
    } else {
        // 显示专家模式输入
        document.getElementById('guided-input').style.display = 'none';
        document.getElementById('expert-input').style.display = 'block';
    }
    
    // 显示返回按钮
    document.getElementById('back-to-mode').style.display = 'block';
    
    this.currentMode = mode;
    }

    showModeSelection() {
    // 显示模式选择
    document.querySelector('.mode-selection').style.display = 'flex';
    
    // 隐藏输入区域
    document.getElementById('guided-input').style.display = 'none';
    document.getElementById('expert-input').style.display = 'none';
    document.getElementById('back-to-mode').style.display = 'none';
    
    this.currentMode = null;
    }

    async showAllSpreads() {
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/get_all_spreads');
            const data = await response.json();
            
            if (response.ok) {
                this.displayAllSpreads(data.spreads);
                this.showSection('spread-section');
            } else {
                this.showMessage(data.error || '获取牌阵失败', 'error');
            }
        } catch (error) {
            this.showMessage('网络错误，请重试', 'error');
            console.error('Error:', error);
        } finally {
            this.showLoading(false);
        }
    }

    displayAllSpreads(spreads) {
        const recommendedContainer = document.getElementById('recommended-spreads');
        const allContainer = document.getElementById('all-spreads');
        
        // 隐藏推荐区域标题
        recommendedContainer.parentElement.querySelector('h2').style.display = 'none';
        recommendedContainer.innerHTML = '';
        
        // 显示所有牌阵
        allContainer.parentElement.querySelector('h3').textContent = '选择牌阵';
        allContainer.innerHTML = '';
        Object.entries(spreads).forEach(([key, spread]) => {
            const spreadElement = this.createSpreadElement({...spread, key}, false);
            allContainer.appendChild(spreadElement);
        });
    }

    // 修改selectSpread方法支持专家模式
    async selectSpread(spreadKey) {
        let question = '';
        
        if (this.currentMode === 'guided') {
            question = document.getElementById('question-input').value.trim();
        } else {
            question = document.getElementById('optional-question').value.trim();
        }
        
        this.showLoading(true);
        
        try {
            const response = await fetch('/api/draw_cards', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    question, 
                    spread_key: spreadKey,
                    mode: this.currentMode || 'guided'
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.currentReading = data;
                this.displayCards(data);
                this.showSection('cards-section');
            } else {
                this.showMessage(data.error || '抽牌失败', 'error');
            }
        } catch (error) {
            this.showMessage('网络错误，请重试', 'error');
            console.error('Error:', error);
        } finally {
            this.showLoading(false);
        }
    }

    // 修改newReading方法
    newReading() {
        document.getElementById('question-input').value = '';
        document.getElementById('optional-question').value = '';
        this.currentReading = null;
        this.currentMode = null;
        this.showModeSelection();
        this.showSection('question-section');
        this.updateNavigation(document.getElementById('nav-home'));
    }

    showSection(sectionId) {
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(sectionId).classList.add('active');
    }

    updateNavigation(activeBtn) {
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        activeBtn.classList.add('active');
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        if (show) {
            loading.classList.remove('hidden');
        } else {
            loading.classList.add('hidden');
        }
    }

    showMessage(message, type = 'info') {
        const messageEl = document.getElementById('message');
        messageEl.textContent = message;
        messageEl.className = `message ${type}`;
        messageEl.classList.remove('hidden');
        
        setTimeout(() => {
            messageEl.classList.add('hidden');
        }, 3000);
    }
}

// 初始化应用
const app = new TarotApp();