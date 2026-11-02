#%matplotlib inline
import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from IPython.display import HTML
from scipy.stats import poisson

# 1. 초기 시뮬레이션 환경 변수 설정
tstep = 1          # 단위시간
prarr = 1/3        # 고객이 1분 안에 도착할 확률
mean = 4           # 평균 서비스 시간 (포아송 분포)
tlimit = 100       # 총 시뮬레이션 수행시간

# 상태 저장용 글로벌 변수
state = {
    'time': 0,
    'queue': 0,
    'totarr': 0,
    'tpump':[0]*2,
    'arrive': 0,
    'history_time': [],
    'history_queue': []
}

# 2. 애니메이션을 위한 시각화 셋업 (Plot 창 설정)
fig, (ax_sim, ax_graph) = plt.subplots(2, 1, figsize=(10, 8), gridspec_kw={'height_ratios': [1.2, 1]})
plt.subplots_adjust(hspace=0.4)

def update_simulation(frame):
    """ 매 프레임(시간 tstep)마다 호출되어 상태를 업데이트하고 그림을 그리는 함수 """
    if state['time'] >= tlimit:
        return
    
    # --- [시뮬레이션 로직 진행] ---
    state['time'] += tstep
    state['arrive'] = 0
    u = random.random()

    # 고객 도착여부 확인
    if u < prarr * tstep:
        state['arrive'] = 1
        state['queue'] += 1
        state['totarr'] += 1

    # 봉사창구 업데이트
    for i in range(2):
        if state['tpump'][i] > 0:
            state['tpump'][i] -= tstep
            if state['tpump'][i] < 0:
                state['tpump'][i] = 0

        if state['tpump'][i] == 0 and state['queue'] != 0:
            state['queue'] -= 1
            # poisson.rvs(mean, 1)은 리스트를 반환하므로 첫 항목 추출
            state['tpump'][i] = int(poisson.rvs(mean, size=1)[0])

    # 그래프용 기록 데이터 누적
    state['history_time'].append(state['time'])
    state['history_queue'].append(state['queue'])

    # --- [2D 그래픽 렌더링] ---
    ax_sim.clear()
    ax_sim.set_xlim(-2, 12)
    ax_sim.set_ylim(-3, 3)
    ax_sim.axis('off')
    ax_sim.set_title(f"Time: {state['time']} min | Total Arrived: {state['totarr']}", fontsize=14, fontweight='bold')

    # ① 봉사 창구 2개 그리기 (네모 상자)
    for i in range(2):
        y_pos = 1 if i == 0 else -1
        is_busy = state['tpump'][i] > 0
        box_color = 'tomato' if is_busy else 'chartreuse'
        text_color = 'white' if is_busy else 'black'
        
        # 창구 사각형
        rect = plt.Rectangle((8, y_pos - 0.5), 2.5, 1.0, facecolor=box_color, edgecolor='black', lw=2)
        ax_sim.add_patch(rect)
        
        # 창구 텍스트 상태 정보
        status_txt = f"BUSY ({state['tpump'][i]}m)" if is_busy else "IDLE"
        ax_sim.text(9.25, y_pos, f"Pump {i+1}\n{status_txt}", 
                    ha='center', va='center', color=text_color, fontweight='bold', fontsize=10)

    # ② 대기 행렬(Queue) 그리기 (사람 모양 대용 원형 점들)
    # 창구 직전 위치(X=6)부터 왼쪽으로 줄을 서는 형태로 구현
    for q_idx in range(state['queue']):
        x_pos = 6 - (q_idx * 0.8)
        if x_pos < -1: # 화면을 벗어나면 생략
            break
        circle = plt.Circle((x_pos, 0), 0.25, color='royalblue', edgecolor='black', lw=1.5)
        ax_sim.add_patch(circle)
        
    # 대기자가 너무 많을 때 생략 표시 및 총 대기 수 표기
    ax_sim.text(6.5, 0, "◀ Entrance", ha='left', va='center', fontsize=11, color='dimgray')
    if state['queue'] > 0:
        ax_sim.text(6, 0.5, f"Waiting: {state['queue']}", ha='right', va='bottom', fontsize=11, color='blue', fontweight='bold')

    # ③ 방금 도착한 고객 표시 (이벤트 알림용)
    if state['arrive'] == 1:
        ax_sim.text(-1.5, 0, "🆕\nArrived!", ha='center', va='center', color='darkorange', fontsize=10, fontweight='bold')

    # ④ 하단 대기열 길이 실시간 선그래프 업데이트
    ax_graph.clear()
    ax_graph.plot(state['history_time'], state['history_queue'], color='royalblue', lw=2, label='Queue Length')
    ax_graph.set_xlim(0, tlimit)
    ax_graph.set_ylim(0, max(max(state['history_queue'] if state['history_queue'] else [5]), 5) + 2)
    ax_graph.set_xlabel('Time (minutes)')
    ax_graph.set_ylabel('Waiting Customers')
    ax_graph.grid(True, linestyle='--', alpha=0.6)
    ax_graph.legend(loc='upper left')

# 3. 애니메이션 구동 설정 (프레임수 = tlimit)
anim = FuncAnimation(fig, update_simulation, frames=tlimit, interval=300, repeat=False)

# Jupyter Notebook 화면에 비디오 플레이어로 출력
HTML(anim.to_html5_video())