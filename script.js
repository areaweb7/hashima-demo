// スムーズスクロール
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ヘッダーのスクロール時の背景変更
const header = document.querySelector('.header');
let lastScroll = 0;

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 100) {
        header.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
    } else {
        header.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)';
    }
    
    lastScroll = currentScroll;
});

// スクロールアニメーション - 要素が表示されたらフェードイン
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// アニメーション対象の要素を設定
const animateElements = document.querySelectorAll('.feature-card, .strength-card, .facility-card, .workflow-step, .data-step');
animateElements.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
    observer.observe(el);
});

// 数値カウントアップアニメーション（処理能力の数値など）
function animateValue(element, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        const value = Math.floor(progress * (end - start) + start);
        element.textContent = value.toFixed(2) + 'トン/日';
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// 施設のスペック値にホバー効果
const specValues = document.querySelectorAll('.spec-value');
specValues.forEach(el => {
    el.addEventListener('mouseenter', () => {
        el.style.transform = 'scale(1.1)';
        el.style.transition = 'transform 0.3s';
    });
    el.addEventListener('mouseleave', () => {
        el.style.transform = 'scale(1)';
    });
});

// モバイルメニュー（将来的な拡張用）
const createMobileMenu = () => {
    const nav = document.querySelector('.nav');
    const navLinks = nav.querySelectorAll('a');
    
    // 画面幅が768px以下の場合、メニューボタンを追加
    if (window.innerWidth <= 768) {
        const menuButton = document.createElement('button');
        menuButton.className = 'mobile-menu-button';
        menuButton.innerHTML = '☰';
        menuButton.style.cssText = `
            display: block;
            font-size: 1.5rem;
            background: none;
            border: none;
            color: var(--primary-color);
            cursor: pointer;
            padding: 10px;
        `;
        
        const headerContent = document.querySelector('.header-content');
        headerContent.appendChild(menuButton);
        
        menuButton.addEventListener('click', () => {
            nav.style.display = nav.style.display === 'flex' ? 'none' : 'flex';
            nav.style.flexDirection = 'column';
            nav.style.position = 'absolute';
            nav.style.top = '100%';
            nav.style.left = '0';
            nav.style.right = '0';
            nav.style.backgroundColor = 'white';
            nav.style.padding = '20px';
            nav.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
        });
    }
};

// ページ読み込み時に実行
window.addEventListener('load', () => {
    // ヒーローセクションのアニメーション
    const heroContent = document.querySelector('.hero-content');
    if (heroContent) {
        heroContent.style.animation = 'fadeInUp 1s ease-out';
    }
    
    // モバイルメニューの設定
    createMobileMenu();
});

// ウィンドウリサイズ時の処理
let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        location.reload();
    }, 250);
});

// ボタンのクリック時のフィードバック
const buttons = document.querySelectorAll('.btn');
buttons.forEach(button => {
    button.addEventListener('click', function(e) {
        // リップル効果
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.cssText = `
            position: absolute;
            width: ${size}px;
            height: ${size}px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.5);
            left: ${x}px;
            top: ${y}px;
            transform: scale(0);
            animation: ripple 0.6s ease-out;
            pointer-events: none;
        `;
        
        this.style.position = 'relative';
        this.style.overflow = 'hidden';
        this.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    });
});

// リップルアニメーションのスタイルを追加
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// パララックス効果（ヒーローセクション）
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const hero = document.querySelector('.hero');
    if (hero && scrolled < window.innerHeight) {
        hero.style.transform = `translateY(${scrolled * 0.5}px)`;
    }
});

// カードのホバー効果強化
const cards = document.querySelectorAll('.feature-card, .strength-card, .facility-card');
cards.forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
    });
});

// スクロール位置の記憶と復元
window.addEventListener('beforeunload', () => {
    sessionStorage.setItem('scrollPosition', window.pageYOffset);
});

window.addEventListener('load', () => {
    const scrollPosition = sessionStorage.getItem('scrollPosition');
    if (scrollPosition) {
        window.scrollTo(0, parseInt(scrollPosition));
        sessionStorage.removeItem('scrollPosition');
    }
});

// フォームの検証（将来的な拡張用）
const validateForm = (form) => {
    const inputs = form.querySelectorAll('input, textarea');
    let isValid = true;
    
    inputs.forEach(input => {
        if (input.hasAttribute('required') && !input.value.trim()) {
            isValid = false;
            input.style.borderColor = 'red';
        } else {
            input.style.borderColor = '';
        }
    });
    
    return isValid;
};

// コンソールにウェルカムメッセージ
console.log('%c中部第一輸送株式会社 岐阜羽島営業所', 'font-size: 20px; font-weight: bold; color: #0066cc;');
console.log('%cワンストップで実現する、次世代の静脈物流', 'font-size: 14px; color: #666;');
console.log('%chttps://cdy.co.jp/', 'font-size: 12px; color: #00aaff;');

