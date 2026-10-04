import streamlit as st
from PIL import Image
import numpy as np
import io
import os
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import ImageReader
from datetime import datetime

#шрифты
def register_arial_font():
    local_font = "arial.ttf"
    if os.path.exists(local_font):
        try:
            pdfmetrics.registerFont(TTFont('ArialCustom', local_font))
            return 'ArialCustom'
        except:
            pass
            
    win_path = "C:\\Windows\\Fonts\\arial.ttf"
    if os.path.exists(win_path):
        try:
            pdfmetrics.registerFont(TTFont('ArialCustom', win_path))
            return 'ArialCustom'
        except:
            pass

    linux_paths = [
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    ]
    for path in linux_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('ArialCustom', path))
                return 'ArialCustom'
            except:
                pass

    mac_path = "/Library/Fonts/Arial.ttf"
    if os.path.exists(mac_path):
        try:
            pdfmetrics.registerFont(TTFont('ArialCustom', mac_path))
            return 'ArialCustom'
        except:
            pass

    return 'Helvetica'

#конфигурация
INDEX_CONFIG = {
    "NDVI": {
        "desc": "Normalized Difference Vegetation Index",
        "classes": [
            {"name": "Здания/Вода/Пусто", "rgb": [255, 0, 0], "weight": 1.0, "score": 0, "rec": "Скорректировать цифровой контур поля. Исключить непродуктивные зоны из страховой базы. Задокументировать границы техногенных участков."},
            {"name": "Открытая почва", "rgb": [237, 160, 0], "weight": 0.7, "score": 1, "rec": "Провести полевую оценку густоты стояния. Выполнить анализ почвы на влажность. Рассмотреть локальный подсев. Скорректировать прогноз урожайности."},
            {"name": "Слабая растительность", "rgb": [255, 255, 0], "weight": 0.3, "score": 2, "rec": "Внести быстроусвояемые азотные удобрения. Оптимизировать график орошения. Провести мониторинг вредителей. Выполнить листовую диагностику питания."},
            {"name": "Умеренная растительность", "rgb": [36, 202, 0], "weight": 0.0, "score": 4, "rec": "Продолжить плановые агротехнические операции. Поддерживать баланс питания и влажности. Проводить профилактические обработки СЗР. Контролировать равномерность развития."},
            {"name": "Здоровая растительность", "rgb": [0, 127, 0], "weight": 0.0, "score": 5, "rec": "Сохранить текущий режим обслуживания. Усилить мониторинг риска полегания. Подготовить технику для уборки. Скорректировать логистику под высокую урожайность."}
        ]
    },
    "NDMI": {
        "desc": "Normalized Difference Moisture Index (Индекс влажности)",
        "classes": [
            {"name": "Почва без растительности", "rgb": [255, 0, 0], "weight": 1.0, "score": 0, "rec": "Критическое отсутствие вегетации. Проверить границы поля. Исключить техногенные зоны из расчета."},
            {"name": "Почти отсутствующий покров", "rgb": [255, 105, 0], "weight": 0.9, "score": 1, "rec": "Критический водный стресс или гибель посевов. Срочно оценить необходимость пересева или списания участка."},
            {"name": "Очень низкий покров", "rgb": [255, 144, 0], "weight": 0.8, "score": 2, "rec": "Сильнейший дефицит влаги. Требуется экстренный полив (если возможно) или оценка потерь урожайности."},
            {"name": "Сухой покров растительности", "rgb": [255, 179, 0], "weight": 0.6, "score": 3, "rec": "Высокий уровень стресса. Оптимизировать орошение. Рассмотреть внесение антистрессовых препаратов."},
            {"name": "Низкий покров (высокий стресс)", "rgb": [255, 253, 0], "weight": 0.4, "score": 4, "rec": "Умеренный водный стресс. Контролировать влажность почвы. Скорректировать график полива."},
            {"name": "Средний покров (средний стресс)", "rgb": [224, 255, 0], "weight": 0.2, "score": 5, "rec": "Незначительный стресс. Поддерживать текущий режим увлажнения. Мониторинг прогноза осадков."},
            {"name": "Средне-высокий покров", "rgb": [157, 255, 0], "weight": 0.1, "score": 6, "rec": "Хорошее увлажнение. Стандартный уход. Следить за равномерностью распределения влаги."},
            {"name": "Высокий покров (нет стресса)", "rgb": [110, 255, 0], "weight": 0.0, "score": 7, "rec": "Оптимальная влагообеспеченность. Продолжать плановые агротехнические мероприятия."},
            {"name": "Очень высокий покров", "rgb": [71, 183, 0], "weight": 0.0, "score": 8, "rec": "Отличное состояние. Максимальная биомасса. Контроль на предмет переувлажнения в низинах."},
            {"name": "Полный покров (риск переувлажнения)", "rgb": [20, 117, 0], "weight": 0.0, "score": 9, "rec": "Насыщение влагой. Оценить риск заболачивания или развития грибных заболеваний в густых посевах."}
        ]
    },
    "IPVI": {
        "desc": "Infrared Percentage Vegetation Index",
        "classes": [
            {"name": "Нездоровая растительность", "rgb": [255, 66, 0], "weight": 1.0, "score": 0, "rec": "Критическое угнетение посевов. Выявить причины (болезни, засуха, вредители). Рассмотреть вопрос о страховом случае."},
            {"name": "Здоровая зеленая растительность", "rgb": [75, 149, 0], "weight": 0.0, "score": 5, "rec": "Нормальное развитие культуры. Поддерживать стандартный режим агротехники."}
        ]
    },
    "GNDVI": {
        "desc": "Green NDVI (Индекс хлорофилла)",
        "classes": [
            {"name": "Отсутствие растительности / Вода", "rgb": [255, 66, 0], "weight": 1.0, "score": 0, "rec": "Полное отсутствие вегетации или водные объекты. Исключить из страховой площади."},
            {"name": "Крайне разреженные всходы", "rgb": [255, 161, 0], "weight": 0.9, "score": 1, "rec": "Критически низкая густота. Оценить необходимость пересева. Высокий риск потери урожая."},
            {"name": "Стрессовая растительность", "rgb": [250, 222, 0], "weight": 0.7, "score": 2, "rec": "Дефицит азота или хлорофилла. Требуется срочная листовая подкормка и диагностика причин стресса."},
            {"name": "Умеренная растительность", "rgb": [241, 255, 0], "weight": 0.4, "score": 3, "rec": "Средний уровень развития. Контролировать питание (азот/магний). Мониторинг динамики роста."},
            {"name": "Здоровая растительность", "rgb": [67, 213, 0], "weight": 0.1, "score": 4, "rec": "Хорошее содержание хлорофилла. Поддерживать текущий уровень агрофона. Профилактика болезней."},
            {"name": "Густая растительность (Отлично)", "rgb": [0, 87, 0], "weight": 0.0, "score": 5, "rec": "Максимальная фотосинтетическая активность. Оптимальное состояние. Готовность к высокой урожайности."}
        ]
    },
    "RVI": {
        "desc": "Ratio Vegetation Index",
        "classes": [
            {"name": "Открытая почва / Отсутствие растительности", "rgb": [255, 0, 0], "weight": 1.0, "score": 0, "rec": "Отсутствие вегетационного покрова. Проверить границы поля и наличие посевов."},
            {"name": "Разреженная / Стрессовая растительность", "rgb": [243, 255, 0], "weight": 0.8, "score": 1, "rec": "Критически низкая биомасса или сильный стресс. Требуется срочная диагностика и вмешательство."},
            {"name": "Среднеразвитая растительность", "rgb": [109, 220, 0], "weight": 0.3, "score": 3, "rec": "Удовлетворительное развитие. Контроль питания и влажности для предотвращения деградации."},
            {"name": "Густая / Здоровая растительность", "rgb": [0, 127, 0], "weight": 0.0, "score": 5, "rec": "Высокая продуктивность. Поддержание оптимальных условий для максимизации урожая."}
        ]
    },
    "SAVI": {
        "desc": "Soil Adjusted Vegetation Index (С поправкой на почву)",
        "classes": [
            {"name": "Открытая почва / Отсутствие растительности", "rgb": [255, 0, 0], "weight": 1.0, "score": 0, "rec": "Полное отсутствие вегетации. Исключить из расчета или оценить необходимость пересева."},
            {"name": "Разреженная растительность", "rgb": [243, 169, 0], "weight": 0.8, "score": 1, "rec": "Низкая густота стояния. Высокий риск влияния сорняков и эрозии. Требуется контроль всхожести."},
            {"name": "Водный стресс растительности", "rgb": [229, 255, 0], "weight": 0.5, "score": 2, "rec": "Признаки дефицита влаги. Оптимизировать полив. Рассмотреть внесение антистрессантов."},
            {"name": "Здоровая и густая растительность", "rgb": [0, 199, 0], "weight": 0.0, "score": 4, "rec": "Отличное состояние посевов. Поддерживать текущий режим агротехники."}
        ]
    }
}

MONTH_HEALTH_NORMS = {"Май": 40, "Июнь": 70, "Июль": 80, "Август": 60, "Сентябрь": 50}
MONTH_DEVIATION_THRESHOLDS = {"Май": 70, "Июнь": 20, "Июль": 30, "Август": 40, "Сентябрь": 60}
PAYOUT_THRESHOLDS = {"start": 20, "medium": 40, "high": 60}

#анализ
def analyze_change_and_classes(img_start_pil, img_current_pil, classes_config, month_start, month_current):
    arr_start = np.array(img_start_pil.resize(img_current_pil.size, Image.LANCZOS).convert("RGB"))
    arr_current = np.array(img_current_pil.convert("RGB"))
    
    brightness = np.sum(arr_current, axis=-1)
    non_background_mask = brightness < 700 
    total_useful_pixels = np.count_nonzero(non_background_mask)
    if total_useful_pixels == 0: raise ValueError("Нет полезных данных")

    start_scores = np.zeros(arr_start.shape[:2], dtype=np.int8)
    current_scores = np.zeros(arr_current.shape[:2], dtype=np.int8)
    current_class_masks = {}
    start_class_stats = {cls["name"]: 0 for cls in classes_config}
    current_class_stats = {cls["name"]: 0 for cls in classes_config}
    TOLERANCE = 60 
    
    for cls in classes_config:
        target = np.array(cls["rgb"], dtype=int)
        mask_s = np.all(np.abs(arr_start.astype(int) - target) <= TOLERANCE, axis=-1) & non_background_mask
        start_scores[mask_s] = cls["score"]; start_class_stats[cls["name"]] = np.count_nonzero(mask_s)
        mask_c = np.all(np.abs(arr_current.astype(int) - target) <= TOLERANCE, axis=-1) & non_background_mask
        current_scores[mask_c] = cls["score"]; current_class_masks[cls["name"]] = mask_c; current_class_stats[cls["name"]] = np.count_nonzero(mask_c)

    degradation_mask = (current_scores < start_scores) & non_background_mask
    total_degraded_pixels = np.count_nonzero(degradation_mask)
    pct_degradation_of_field = (total_degraded_pixels / total_useful_pixels * 100) if total_useful_pixels > 0 else 0
    current_health_pct = (np.count_nonzero((current_scores >= 4) & non_background_mask) / total_useful_pixels * 100) if total_useful_pixels > 0 else 0

    visual_overlay = arr_current.copy()
    visual_overlay[~degradation_mask] = (visual_overlay[~degradation_mask] * 0.2).astype(np.uint8)
    visual_overlay[~non_background_mask] = [0, 0, 0] 

    class_stats_degraded = {cls["name"]: 0 for cls in classes_config}
    weighted_damage_sum = 0.0; degradation_details = []

    if total_degraded_pixels > 0:
        for cls in classes_config:
            final_zone = degradation_mask & current_class_masks[cls["name"]]
            count = np.count_nonzero(final_zone)
            if count > 0:
                class_stats_degraded[cls["name"]] += count
                weighted_damage_sum += (count / total_degraded_pixels) * cls["weight"]
                visual_overlay[final_zone] = cls["rgb"]
                degradation_details.append({"name": cls["name"], "area_pct": (count / total_useful_pixels) * 100, "weight": cls["weight"]})

    final_risk_score = pct_degradation_of_field * (weighted_damage_sum if weighted_damage_sum > 0 else 1.0)
    start_pct = {k: (v / total_useful_pixels * 100) for k, v in start_class_stats.items()}
    current_pct = {k: (v / total_useful_pixels * 100) for k, v in current_class_stats.items()}
    results_report = {}
    for name, count in class_stats_degraded.items():
        if count > 0:
            cls_data = next(c for c in classes_config if c["name"] == name)
            results_report[name] = {"pct": (count/total_degraded_pixels)*100, "rec": cls_data["rec"], "weight": cls_data["weight"]}

    start_deviation_pct = (np.count_nonzero((start_scores <= 1) & non_background_mask) / total_useful_pixels * 100) if total_useful_pixels > 0 else 0
    current_deviation_pct = (np.count_nonzero((current_scores <= 1) & non_background_mask) / total_useful_pixels * 100) if total_useful_pixels > 0 else 0

    return (results_report, final_risk_score, visual_overlay, current_health_pct, 
            MONTH_HEALTH_NORMS[month_current], pct_degradation_of_field, 
            start_pct, current_pct, degradation_details, weighted_damage_sum, 
            start_deviation_pct, current_deviation_pct, current_class_stats, total_useful_pixels)

#графики
def _setup_matplotlib(): plt.rcParams.update({'figure.max_open_warning': 0, 'font.family': 'sans-serif'})

def create_comparison_chart(start_pct, current_pct, classes_config):
    _setup_matplotlib()
    labels, start_vals, current_vals, colors = [], [], [], []
    for cls in classes_config:
        s, c = start_pct.get(cls["name"], 0), current_pct.get(cls["name"], 0)
        if s > 0.5 or c > 0.5: labels.append(cls["name"]); start_vals.append(s); current_vals.append(c); colors.append(f"#{cls['rgb'][0]:02x}{cls['rgb'][1]:02x}{cls['rgb'][2]:02x}")
    if not labels: return b''
    fig, ax = plt.subplots(figsize=(8, 4)); x = np.arange(len(labels)); w = 0.35
    r1 = ax.bar(x - w/2, start_vals, w, color='#CCCCCC', edgecolor='white')
    r2 = ax.bar(x + w/2, current_vals, w, color=colors, edgecolor='white')
    ax.set_ylabel('Доля площади (%)', fontsize=10); ax.set_title('Динамика структуры поля', fontsize=12, fontweight='bold')
    ax.set_xticks(x); ax.set_xticklabels(labels, rotation=15, ha="right", fontsize=8); ax.legend(loc='upper right', fontsize=8); ax.set_ylim(0, 100)
    for rect in [*r1, *r2]:
        if rect.get_height() > 1: ax.annotate(f'{rect.get_height():.1f}%', (rect.get_x()+rect.get_width()/2, rect.get_height()), xytext=(0,3), textcoords="offset points", ha='center', va='bottom', fontsize=7)
    buf = io.BytesIO(); plt.tight_layout(); plt.savefig(buf, format='PNG', dpi=100, facecolor='white'); plt.close(fig); buf.seek(0); return buf.getvalue()

def create_field_structure_chart(current_pct_dict, classes_config):
    _setup_matplotlib()
    labels, sizes, colors = [], [], []
    for cls in classes_config:
        val = current_pct_dict.get(cls["name"], 0)
        if val > 0.5: labels.append(cls["name"]); sizes.append(val); colors.append(f"#{cls['rgb'][0]:02x}{cls['rgb'][1]:02x}{cls['rgb'][2]:02x}")
    if not labels: return b''
    fig, ax = plt.subplots(figsize=(5, 5)); ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8})
    ax.set_title('Структура поля', fontsize=11, fontweight='bold')
    buf = io.BytesIO(); plt.savefig(buf, format='PNG', dpi=100, facecolor='white', bbox_inches='tight'); plt.close(fig); buf.seek(0); return buf.getvalue()

def create_deviation_chart(current_class_stats, total_pixels):
    _setup_matplotlib()
    labels, values = [], []
    
    crit_classes = []
    if "Здания/Вода/Пусто" in current_class_stats: # NDVI
        crit_classes = [("Здания/Вода/Пусто", '#FF0000'), ("Открытая почва", '#ED8A00')]
    elif "Почва без растительности" in current_class_stats: # NDMI
        crit_classes = [("Почва без растительности", '#FF0000'), ("Почти отсутствующий покров", '#FF6900')]
    elif "Нездоровая растительность" in current_class_stats: # IPVI
        crit_classes = [("Нездоровая растительность", '#FF4200')]
    elif "Отсутствие растительности / Вода" in current_class_stats: # GNDVI
        crit_classes = [("Отсутствие растительности / Вода", '#FF4200'), ("Крайне разреженные всходы", '#FFA100')]
    elif "Открытая почва / Отсутствие растительности" in current_class_stats: # RVI / SAVI
        # Для SAVI добавляем еще и стресс (желтый), так как score=2 тоже низкий
        if "Водный стресс растительности" in current_class_stats:
             crit_classes = [("Открытая почва / Отсутствие растительности", '#FF0000'), ("Разреженная растительность", '#F3A900'), ("Водный стресс растительности", '#E5FF00')]
        else:
             crit_classes = [("Открытая почва / Отсутствие растительности", '#FF0000'), ("Разреженная / Стрессовая растительность", '#F3FF00')]
    else:
        for idx_name, cfg in INDEX_CONFIG.items():
             if cfg["classes"]:
                 bad_cls = cfg["classes"][0]
                 crit_classes = [(bad_cls["name"], f"#{bad_cls['rgb'][0]:02x}{bad_cls['rgb'][1]:02x}{bad_cls['rgb'][2]:02x}")]
                 break

    for name, col in crit_classes:
        cnt = current_class_stats.get(name, 0)
        if cnt > 0:
            pct = (cnt / total_pixels * 100) if total_pixels > 0 else 0
            if pct > 0.5: labels.append(name); values.append(pct)
            
    if not labels:
        fig, ax = plt.subplots(figsize=(5, 5)); ax.axis('off'); ax.text(0.5, 0.5, 'Нет критических\nотклонений', ha='center', va='center', fontsize=12, color='green', fontweight='bold')
        ax.set_title('Отклонения', fontsize=11, fontweight='bold')
        buf = io.BytesIO(); plt.savefig(buf, format='PNG', dpi=100, facecolor='white'); plt.close(fig); buf.seek(0); return buf.getvalue()
        
    fig, ax = plt.subplots(figsize=(5, 5)); bars = ax.bar(labels, values, color=[c for _, c in crit_classes[:len(labels)]], edgecolor='black', linewidth=1)
    ax.set_ylabel('% площади', fontsize=9); ax.set_title('Отклонения', fontsize=11, fontweight='bold'); ax.set_ylim(0, max(values)*1.3 if max(values)>0 else 10)
    ax.tick_params(axis='x', labelsize=8, rotation=15)
    for b, v in zip(bars, values): ax.annotate(f'{v:.1f}%', (b.get_x()+b.get_width()/2, v), xytext=(0,3), textcoords="offset points", ha='center', va='bottom', fontsize=9)
    buf = io.BytesIO(); plt.tight_layout(); plt.savefig(buf, format='PNG', dpi=100, facecolor='white', bbox_inches='tight'); plt.close(fig); buf.seek(0); return buf.getvalue()

#PDF:отчет
def create_insurance_pdf(month_start, month_current, risk_score, payout, insured_amount, index_name, class_results, health_pct, norm_pct, pct_degr, start_pct, current_pct, classes_config, visual_mask_bytes, degradation_details, avg_weight, start_dev_pct, curr_dev_pct, thresh_start, thresh_curr):
    buffer = io.BytesIO(); c = canvas.Canvas(buffer, pagesize=A4); width, height = A4; font_name = register_arial_font()
    
    c.setFillColor(HexColor("#2E8B57")); c.rect(0, height - 2.5*cm, width, 2.5*cm, fill=True, stroke=False)
    c.setFillColor(white); c.setFont(font_name, 22); c.drawCentredString(width/2, height - 1.3*cm, "ОТЧЕТ АГРОНОМИЧЕСКОГО АНАЛИЗА")
    c.setFont(font_name, 10); c.drawString(2*cm, height - 2.0*cm, f"Регион: Данковский район | Индекс: {index_name}")
    c.drawRightString(width - 2*cm, height - 2.0*cm, f"Дата: {st.session_state.get('date', '20.05.2026')}")

    y = height - 4.2*cm; c.setFillColor("#000000"); c.setFont(font_name, 14); c.drawString(2*cm, y, "1. Динамика состояния посевов")
    warns = []
    if start_dev_pct > thresh_start: warns.append(f"⚠️ {month_start}: Отклонения {start_dev_pct:.1f}% > {thresh_start}%")
    if curr_dev_pct > thresh_curr: warns.append(f"⚠️ {month_current}: Отклонения {curr_dev_pct:.1f}% > {thresh_curr}%")
    if warns:
        c.setFillColor(HexColor("#D32F2F")); c.setFont(font_name, 11); wy = y - 0.6*cm
        for w in warns: c.drawString(2*cm, wy, w); wy -= 0.5*cm
        c.setFillColor("#000000"); c.setFont(font_name, 11); y -= (len(warns)*0.5 + 0.4)*cm

    chart = create_comparison_chart(start_pct, current_pct, classes_config)
    if chart: c.drawImage(ImageReader(io.BytesIO(chart)), 2*cm, y - 4.5*cm, width=17*cm, height=4*cm, preserveAspectRatio=True, mask='auto')
    
    y -= 6.5*cm; c.setFont(font_name, 14); c.drawString(2*cm, y, "2. Карта выявленных ухудшений")
    c.setFont(font_name, 9); c.drawString(2*cm, y - 0.5*cm, "Подсвечены зоны ухудшения относительно базового снимка.")
    if visual_mask_bytes: c.drawImage(ImageReader(io.BytesIO(visual_mask_bytes)), 2*cm, y - 5.0*cm, width=17*cm, height=4*cm, preserveAspectRatio=True, mask='auto')
    
    y -= 6.2*cm 
    block_h = 6.0*cm 
    c.setFillColor(HexColor("#F9F9F9")); c.rect(2*cm, y - block_h, 17*cm, block_h, fill=True, stroke=True); c.setStrokeColor("#CCCCCC")
    
    c.setFillColor("#000000"); c.setFont(font_name, 14); c.drawString(2.5*cm, y - 0.7*cm, "3. Детальный расчет риска")
    c.setFont(font_name, 10); c.drawString(2.5*cm, y - 1.3*cm, "Деградация по классам:")
    
    cy = y - 1.8*cm
    for d in degradation_details: 
        c.drawString(3.0*cm, cy, f"- {d['name']}: {d['area_pct']:.2f}%")
        cy -= 0.5*cm
        
    c.drawString(2.5*cm, cy - 0.3*cm, f"Средний взвешенный ущерб: {avg_weight:.2f}")
    c.drawString(2.5*cm, cy - 0.8*cm, f"Общая площадь ухудшений: {pct_degr:.2f}%")
    
    c.line(2.5*cm, cy - 1.2*cm, 18*cm, cy - 1.2*cm)
    c.setFont(font_name, 11); c.drawString(2.5*cm, cy - 1.8*cm, f"ИТОГОВЫЙ ИНДЕКС РИСКА: {risk_score:.2f}%")
    c.drawString(2.5*cm, cy - 2.3*cm, f"({pct_degr:.2f}% × {avg_weight:.2f})")

    fy = y - block_h - 1.5*cm 
    c.setFont(font_name, 12); c.drawString(2.5*cm, fy, f"Страховая сумма: {insured_amount:,.0f} руб.")
    c.setFont(font_name, 18); c.setFillColor(HexColor("#D32F2F")); c.drawString(2.5*cm, fy - 0.8*cm, "ИТОГО К ВЫПЛАТЕ:")
    c.drawRightString(18.5*cm, fy - 0.8*cm, f"{payout:,.0f} руб.")
    
    # ✅ ПОДВАЛ PDF
    c.setFillColor("#555555")
    c.setFont(font_name, 8)
    current_year = datetime.now().year
    c.drawCentredString(width / 2, 1.5*cm, f"© {current_year} Система АгроСтрахования. Все права защищены.")
    c.drawCentredString(width / 2, 1.0*cm, "Разработано в рамках ВКР | Не является публичной офертой")
    
    c.save(); buffer.seek(0); return buffer.getvalue()

#PDF:рекомендации
def create_recommendation_pdf(index_name, class_results, month, health_pct, norm_pct, current_class_stats, total_pixels):
    buffer = io.BytesIO(); c = canvas.Canvas(buffer, pagesize=A4); width, height = A4; font_name = register_arial_font()
    c.setFillColor(HexColor("#FF9800")); c.rect(0, height - 2.2*cm, width, 2.2*cm, fill=True, stroke=False)
    c.setFillColor("#FFFFFF"); c.setFont(font_name, 22); c.drawCentredString(width/2, height - 1.1*cm, "АГРОНОМИЧЕСКИЕ РЕКОМЕНДАЦИИ")
    c.setFont(font_name, 10); c.drawString(2*cm, height - 1.8*cm, f"Индекс: {index_name} | Месяц: {month}")
    
    y = height - 3.2*cm; c.setFillColor("#000000"); c.setFont(font_name, 14); c.drawString(2*cm, y, "1. ОБЩАЯ ОЦЕНКА СОСТОЯНИЯ")
    y -= 0.5*cm; c.setFont(font_name, 11); c.drawString(2*cm, y, f"Здоровье: {health_pct:.1f}% (Норма: {norm_pct}%)")
    y -= 0.4*cm; c.setFillColor(HexColor("#D32F2F") if health_pct < norm_pct else HexColor("#2E8B57"))
    c.drawString(2*cm, y, "Не достигает нормы!" if health_pct < norm_pct else "В пределах нормы"); c.setFillColor("#000000")

    y_charts_top = height - 6*cm 
    chart_w = 9*cm 
    chart_h = 7*cm 
    
    c.setFont(font_name, 14)
    c.drawString(2*cm, y_charts_top + 0.8*cm, "2. СТРУКТУРА")
    c.drawString(11*cm, y_charts_top + 0.8*cm, "3. ОТКЛОНЕНИЯ")
    
    pct_dict = {k: (v/total_pixels*100) for k,v in current_class_stats.items()}
    
    img_struct = create_field_structure_chart(pct_dict, INDEX_CONFIG[index_name]["classes"])
    if img_struct: c.drawImage(ImageReader(io.BytesIO(img_struct)), 2*cm, y_charts_top - chart_h, width=chart_w, height=chart_h, preserveAspectRatio=True, mask='auto')
    
    img_dev = create_deviation_chart(current_class_stats, total_pixels)
    if img_dev: c.drawImage(ImageReader(io.BytesIO(img_dev)), 10.5*cm, y_charts_top - chart_h, width=chart_w, height=chart_h, preserveAspectRatio=True, mask='auto')

    y_txt = y_charts_top - chart_h - 1.0*cm 
    c.setFont(font_name, 14); c.drawString(2*cm, y_txt, "4. РЕКОМЕНДАЦИИ ПО ЗОНАМ")
    y_txt -= 0.6*cm; c.line(2*cm, y_txt, 19*cm, y_txt); y_txt -= 0.5*cm; c.setFont(font_name, 11)
    has_issues = False
    
    for name, data in class_results.items():
        if data['pct'] > 5 and data['weight'] > 0:
            has_issues = True
            if y_txt < 3.5*cm: c.showPage(); c.setFont(font_name, 14); c.drawString(2*cm, height - 2*cm, "4. РЕКОМЕНДАЦИИ (продол.)"); y_txt = height - 2.8*cm; c.setFont(font_name, 11)
            c.setFillColor(HexColor("#D32F2F")); c.drawString(2*cm, y_txt, f"{name} ({data['pct']:.1f}% площади)"); c.setFillColor("#000000"); y_txt -= 0.5*cm
            for p in data['rec'].split('.'):
                p = p.strip(); 
                if not p: continue
                if y_txt < 3*cm: c.showPage(); c.setFont(font_name, 11); y_txt = height - 2*cm
                words = p.split(); line = ""; fl = True
                for w in words:
                    if len(line)+len(w)+1 <= 75: line += " "+w if line else w
                    else:
                        if line: c.drawString(2.5*cm, y_txt, ("• "+line) if fl else ("  "+line)); y_txt -= 0.4*cm; fl=False
                        line = w
                if line: c.drawString(2.5*cm, y_txt, ("• "+line) if fl else ("  "+line)); y_txt -= 0.4*cm
            y_txt -= 0.3*cm
            
    if not has_issues:
        if y_txt < 3.5*cm: c.showPage(); y_txt = height - 2.5*cm
        c.setFillColor(HexColor("#2E8B57")); c.setFont(font_name, 12); c.drawString(2*cm, y_txt, "Критических ухудшений не выявлено."); c.setFillColor("#000000"); y_txt -= 0.6*cm

    if y_txt < 4.5*cm: c.showPage(); y_txt = height - 2.5*cm
    c.setFont(font_name, 14); c.drawString(2*cm, y_txt, "5. ОБЩИЕ РЕКОМЕНДАЦИИ"); y_txt -= 0.6*cm; c.setFont(font_name, 11)
    for r in ["• Мониторинг каждые 7-10 дней", "• Журнал агротехнических мероприятий", "• Внеплановое обследование при ухудшении"]:
        c.drawString(2*cm, y_txt, r); y_txt -= 0.45*cm
        
    c.setFillColor("#555555")
    c.setFont(font_name, 8)
    current_year = datetime.now().year
    c.drawCentredString(width / 2, 2.0*cm, f"© {current_year} Система АгроСтрахования. Все права защищены.")
    c.drawCentredString(width / 2, 1.5*cm, "Разработано в рамках ВКР | Не является публичной офертой")
    
    c.save(); buffer.seek(0); return buffer.getvalue()

#интерфейс
st.set_page_config(page_title="АгроСтрахование", page_icon="🌾", layout="wide")
if 'date' not in st.session_state:
    st.session_state['date'] = datetime.now().strftime("%d.%m.%Y")

st.markdown("<h1 style='text-align:center;color:#2E8B57;'>🌾 Система АгроСтрахования</h1>", unsafe_allow_html=True)
st.divider()

with st.sidebar:
    st.header("⚙️ Параметры")
    selected_index = st.selectbox("Индекс:", list(INDEX_CONFIG.keys()))
    st.caption(INDEX_CONFIG[selected_index]["desc"])
    col_m1, col_m2 = st.columns(2)
    with col_m1: month_start = st.selectbox("Месяц (База):", list(MONTH_HEALTH_NORMS.keys()), index=0)
    with col_m2: month_current = st.selectbox("Месяц (Сейчас):", list(MONTH_HEALTH_NORMS.keys()), index=2)
    insured_amount = st.number_input("Страховая сумма (руб.):", value=1000000, step=50000)
    st.divider(); st.subheader("Шкала выплат")
    st.text(f"0 – {PAYOUT_THRESHOLDS['start']-1}% риска: 0% выплаты")
    st.text(f"{PAYOUT_THRESHOLDS['start']} – {PAYOUT_THRESHOLDS['medium']-1}% риска: 30% выплаты")
    st.text(f"{PAYOUT_THRESHOLDS['medium']} – {PAYOUT_THRESHOLDS['high']-1}% риска: 60% выплаты")
    st.text(f">= {PAYOUT_THRESHOLDS['high']}% риска: 100% выплаты")

col1, col2 = st.columns(2)
with col1:
    st.subheader("1. Базовый снимок")
    file_start = st.file_uploader("Фото начала сезона", type=["jpg", "png", "jpeg"], key="start")
    if file_start: st.image(Image.open(file_start), use_container_width=True, width=400)
with col2:
    st.subheader("2. Текущий снимок")
    file_current = st.file_uploader("Текущее фото", type=["jpg", "png", "jpeg"], key="current")
    if file_current: st.image(Image.open(file_current), use_container_width=True, width=400)

if file_start and file_current:
    st.divider()
    if st.button("📊 Сравнить снимки и рассчитать", type="primary", use_container_width=True):
        if not INDEX_CONFIG[selected_index]["classes"]: st.error("Классификация для индекса не настроена."); st.stop()
        with st.spinner('Анализ динамики...'):
            try:
                res, risk, mask, health, norm, degr, s_pct, c_pct, details, avg_w, s_dev, c_dev, c_stats, t_pix = analyze_change_and_classes(Image.open(file_start), Image.open(file_current), INDEX_CONFIG[selected_index]["classes"], month_start, month_current)
                
                thresh_s, thresh_c = MONTH_DEVIATION_THRESHOLDS[month_start], MONTH_DEVIATION_THRESHOLDS[month_current]
                warns = []
                if s_dev > thresh_s: warns.append(f"⚠️ {month_start}: Отклонения {s_dev:.1f}% > {thresh_s}%")
                if c_dev > thresh_c: warns.append(f"⚠️ {month_current}: Отклонения {c_dev:.1f}% > {thresh_c}%")
                if warns: st.divider(); 
                for w in warns: st.warning(w); 
                if warns: st.divider()

                payout = insured_amount * (1.0 if risk>=PAYOUT_THRESHOLDS['high'] else 0.6 if risk>=PAYOUT_THRESHOLDS['medium'] else 0.3 if risk>=PAYOUT_THRESHOLDS['start'] else 0)
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Здоровье", f"{health:.1f}%"); m2.metric("Ухудшения", f"{degr:.1f}%")
                m3.metric("Индекс риска", f"{risk:.1f}%"); m4.metric("Выплата", f"{payout:,.0f} руб.")
                
                if risk == 0: st.success("✅ Ухудшений не выявлено.")
                elif risk < PAYOUT_THRESHOLDS['start']: st.warning(f"⚠️ Риск {risk:.1f}% (ниже порога).")
                else: st.error(f"🚨 Риск {risk:.1f}%. Выплата подтверждена.")

                st.image(mask, caption="Зоны ухудшения", use_container_width=True)
                buf = io.BytesIO(); Image.fromarray(mask).save(buf, format="PNG"); mask_bytes = buf.getvalue()
                
                pdf1 = create_insurance_pdf(month_start, month_current, risk, payout, insured_amount, selected_index, res, health, norm, degr, s_pct, c_pct, INDEX_CONFIG[selected_index]["classes"], mask_bytes, details, avg_w, s_dev, c_dev, thresh_s, thresh_c)
                pdf2 = create_recommendation_pdf(selected_index, res, month_current, health, norm, c_stats, t_pix)
                
                b1, b2 = st.columns(2)
    
                with b1: st.download_button("📥 Скачать отчет (PDF)", pdf1, f"Отчет_{selected_index}.pdf", "application/pdf", use_container_width=True)
                with b2: st.download_button("💡 Скачать рекомендации", pdf2, f"Рекомендации_{selected_index}.pdf", "application/pdf", use_container_width=True)
            except Exception as e: st.error(f"Ошибка анализа: {e}")

st.divider()
current_year = datetime.now().year
st.markdown(f"""
<div style='text-align: center; color: #888; font-size: 16px; margin-top: 20px;'>
    © {current_year} Система АгроСтрахования. Все права защищены.<br>
    Разработано в рамках ВКР | Не является публичной офертой
</div>
""", unsafe_allow_html=True)
