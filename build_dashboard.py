import json, os

with open('is_data_precomputed.json', 'r', encoding='utf-8') as f:
    stats = json.load(f)

with open('packed_binary.b64', 'r') as f:
    b64_data = f.read().strip()

with open('packed_meta.json', 'r', encoding='utf-8') as f:
    meta = json.load(f)

with open('thailand_svg_paths.json', 'r', encoding='utf-8') as f:
    svg_paths = json.load(f)

provinces_json = json.dumps(meta['provinces'], ensure_ascii=False)
years_json = json.dumps(meta.get('years', ['2569']), ensure_ascii=False)
stats_json = json.dumps(stats, ensure_ascii=False)
svg_paths_json = json.dumps(svg_paths, ensure_ascii=False)

html_code = f'''<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
    <title>IS Injury Surveillance Dashboard | ระบบเฝ้าระวังการบาดเจ็บแห่งชาติ</title>
    <!-- Google Fonts: Anuphan -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Anuphan:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <!-- Font Awesome 6 Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <!-- Chart.js 4 -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- fflate for high-speed client-side decompression -->
    <script src="https://cdn.jsdelivr.net/npm/fflate@0.8.2/umd/index.js"></script>
    <!-- PapaParse for multi-file CSV import -->
    <script src="https://cdn.jsdelivr.net/npm/papaparse@5.4.1/papaparse.min.js"></script>

    <style>
        :root {{
            --font-family: 'Anuphan', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            --radius-sm: 4px; /* Strict rounded-sm layout as requested */
            
            /* Semantic Color System */
            --primary: #0284c7;
            --primary-dark: #0369a1;
            --primary-light: #e0f2fe;
            --secondary: #0d9488;
            --secondary-light: #ccfbf1;
            
            --danger: #ef4444;
            --danger-dark: #b91c1c;
            --danger-bg: #fee2e2;
            
            --warning: #f59e0b;
            --warning-dark: #b45309;
            --warning-bg: #fef3c7;
            
            --success: #10b981;
            --success-dark: #047857;
            --success-bg: #d1fae5;
            
            --accent: #8b5cf6;
            --accent-bg: #ede9fe;
            
            --bg-body: #f8fafc;
            --bg-card: #ffffff;
            --bg-card-subtle: #f1f5f9;
            --bg-card-hover: #f8fafc;
            
            --navbar-bg: rgba(255, 255, 255, 0.92);
            
            --text-main: #0f172a;
            --text-muted: #64748b;
            --text-light: #94a3b8;
            
            --border-color: #e2e8f0;
            --border-hover: #cbd5e1;
            
            --shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.04);
            --shadow-sm: 0 1px 3px 0 rgb(0 0 0 / 0.08), 0 1px 2px -1px rgb(0 0 0 / 0.06);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.08), 0 2px 4px -2px rgb(0 0 0 / 0.04);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.08), 0 4px 6px -4px rgb(0 0 0 / 0.04);
        }}

        [data-theme="dark"] {{
            --primary: #38bdf8;
            --primary-dark: #0284c7;
            --primary-light: #082f49;
            --secondary: #2dd4bf;
            --secondary-light: #134e4a;
            
            --danger: #f87171;
            --danger-dark: #dc2626;
            --danger-bg: #450a0a;
            
            --warning: #fbbf24;
            --warning-dark: #d97706;
            --warning-bg: #451a03;
            
            --success: #34d399;
            --success-dark: #059669;
            --success-bg: #064e3b;
            
            --accent: #a78bfa;
            --accent-bg: #2e1065;
            
            --bg-body: #0b1120;
            --bg-card: #131d33;
            --bg-card-subtle: #1c2947;
            --bg-card-hover: #223254;
            
            --navbar-bg: rgba(19, 29, 51, 0.92);
            
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --text-light: #64748b;
            
            --border-color: #243452;
            --border-hover: #33486e;
            
            --shadow-xs: 0 1px 2px 0 rgb(0 0 0 / 0.3);
            --shadow-sm: 0 2px 4px 0 rgb(0 0 0 / 0.4);
            --shadow-md: 0 4px 8px -1px rgb(0 0 0 / 0.5);
            --shadow-lg: 0 10px 20px -3px rgb(0 0 0 / 0.6);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: var(--font-family);
            background-color: var(--bg-body);
            color: var(--text-main);
            line-height: 1.5;
            transition: background-color 0.25s ease, color 0.25s ease;
            -webkit-font-smoothing: antialiased;
            overflow-x: hidden;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }}

        /* STICKY TOPBAR / NAVBAR (FIXED AT TOP) */
        .sticky-navbar {{
            position: sticky;
            top: 0;
            left: 0;
            right: 0;
            width: 100%;
            z-index: 1000;
            background: var(--navbar-bg);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border-bottom: 1px solid var(--border-color);
            box-shadow: var(--shadow-sm);
            transition: background-color 0.3s ease, border-color 0.3s ease;
        }}

        .navbar-container {{
            max-width: 1560px;
            margin: 0 auto;
            padding: 10px clamp(14px, 2vw, 24px);
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 14px;
            flex-wrap: wrap;
        }}

        .brand-cluster {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .brand-badge-icon {{
            width: 42px;
            height: 42px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: #ffffff;
            border-radius: var(--radius-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            flex-shrink: 0;
            box-shadow: 0 4px 10px -2px rgba(2, 132, 199, 0.4);
        }}

        .brand-meta h1 {{
            font-size: clamp(1rem, 1.8vw, 1.25rem);
            font-weight: 700;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
            line-height: 1.2;
        }}

        .badge-academic {{
            font-size: 0.68rem;
            font-weight: 600;
            background: var(--primary-light);
            color: var(--primary);
            padding: 2px 8px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--primary);
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }}

        .brand-meta p {{
            font-size: clamp(0.72rem, 1.2vw, 0.8rem);
            color: var(--text-muted);
            margin-top: 2px;
        }}

        .navbar-actions {{
            display: flex;
            align-items: center;
            gap: 8px;
            flex-wrap: wrap;
        }}

        /* Buttons (Strict rounded-sm) */
        .btn {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            padding: 6px 12px;
            font-size: 0.82rem;
            font-weight: 600;
            font-family: inherit;
            border-radius: var(--radius-sm);
            cursor: pointer;
            border: 1px solid transparent;
            transition: all 0.2s ease;
            white-space: nowrap;
            min-height: 34px;
        }}

        .btn-primary {{
            background: var(--primary);
            color: #ffffff;
        }}
        .btn-primary:hover {{
            background: var(--primary-dark);
            transform: translateY(-1px);
        }}

        .btn-outline {{
            background: var(--bg-card);
            border-color: var(--border-color);
            color: var(--text-main);
        }}
        .btn-outline:hover {{
            background: var(--bg-card-subtle);
            border-color: var(--border-hover);
        }}

        .btn-danger-outline {{
            background: var(--bg-card);
            border-color: var(--danger);
            color: var(--danger);
        }}
        .btn-danger-outline:hover {{
            background: var(--danger-bg);
        }}

        .btn-success-outline {{
            background: var(--bg-card);
            border-color: var(--success);
            color: var(--success);
        }}
        .btn-success-outline:hover {{
            background: var(--success-bg);
        }}

        .theme-toggle-btn {{
            width: 34px;
            height: 34px;
            border-radius: var(--radius-sm);
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--bg-card-subtle);
            color: var(--text-main);
            border: 1px solid var(--border-color);
            cursor: pointer;
            font-size: 0.95rem;
            transition: all 0.2s;
        }}
        .theme-toggle-btn:hover {{
            border-color: var(--primary);
        }}

        /* Main Content Container */
        .container {{
            width: 100%;
            max-width: 1560px;
            margin: 0 auto;
            padding: clamp(14px, 2vw, 24px);
            flex: 1;
        }}

        /* REAL-TIME FILTER BAR (ROUNDED-SM) */
        .filter-panel {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            padding: clamp(12px, 1.8vw, 16px);
            margin-bottom: 20px;
            box-shadow: var(--shadow-sm);
        }}

        .filter-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            flex-wrap: wrap;
            gap: 10px;
        }}

        .filter-title {{
            font-size: 0.92rem;
            font-weight: 700;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .filter-stats-badge {{
            font-size: 0.8rem;
            color: var(--text-muted);
            background: var(--bg-card-subtle);
            padding: 4px 10px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-color);
        }}

        .filter-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 10px;
        }}

        .filter-group {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .filter-label {{
            font-size: 0.72rem;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.03em;
        }}

        .filter-select, .filter-input {{
            font-family: inherit;
            font-size: 0.82rem;
            padding: 6px 8px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--border-color);
            background: var(--bg-card);
            color: var(--text-main);
            outline: none;
            transition: all 0.2s;
            width: 100%;
        }}

        .filter-select:focus, .filter-input:focus {{
            border-color: var(--primary);
            box-shadow: 0 0 0 2px rgba(2, 132, 199, 0.15);
        }}

        /* Active Filter Chips */
        .filter-chips-bar {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            align-items: center;
            margin-top: 12px;
            padding-top: 10px;
            border-top: 1px dashed var(--border-color);
        }}

        .chip-label {{
            font-size: 0.76rem;
            font-weight: 600;
            color: var(--text-muted);
        }}

        .filter-chip {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: var(--primary-light);
            color: var(--primary);
            font-size: 0.76rem;
            font-weight: 600;
            padding: 2px 7px;
            border-radius: var(--radius-sm);
            border: 1px solid var(--primary);
        }}

        .filter-chip i.close-btn {{
            cursor: pointer;
            font-size: 0.72rem;
        }}
        .filter-chip i.close-btn:hover {{
            color: var(--danger);
        }}

        /* KPI Grid (rounded-sm) */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr));
            gap: 12px;
            margin-bottom: 22px;
        }}

        .kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            padding: 14px 16px;
            box-shadow: var(--shadow-xs);
            position: relative;
            overflow: hidden;
            transition: all 0.2s ease;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .kpi-card:hover {{
            box-shadow: var(--shadow-sm);
            border-color: var(--border-hover);
            transform: translateY(-2px);
        }}

        .kpi-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: var(--primary);
        }}
        .kpi-card.danger::before {{ background: var(--danger); }}
        .kpi-card.warning::before {{ background: var(--warning); }}
        .kpi-card.success::before {{ background: var(--success); }}
        .kpi-card.accent::before {{ background: var(--accent); }}

        .kpi-top {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 6px;
        }}

        .kpi-label {{
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-muted);
        }}

        .kpi-icon-wrap {{
            width: 30px;
            height: 30px;
            border-radius: var(--radius-sm);
            background: var(--bg-card-subtle);
            color: var(--text-muted);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9rem;
        }}

        .kpi-card.danger .kpi-icon-wrap {{ background: var(--danger-bg); color: var(--danger); }}
        .kpi-card.warning .kpi-icon-wrap {{ background: var(--warning-bg); color: var(--warning); }}
        .kpi-card.success .kpi-icon-wrap {{ background: var(--success-bg); color: var(--success); }}
        .kpi-card.accent .kpi-icon-wrap {{ background: var(--accent-bg); color: var(--accent); }}

        .kpi-number {{
            font-size: clamp(1.4rem, 2.2vw, 1.75rem);
            font-weight: 700;
            color: var(--text-main);
            letter-spacing: -0.02em;
            line-height: 1.15;
            margin: 4px 0;
        }}

        .kpi-footer {{
            font-size: 0.74rem;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 6px;
            flex-wrap: wrap;
        }}

        .badge-pill {{
            font-weight: 700;
            padding: 2px 6px;
            border-radius: var(--radius-sm);
            font-size: 0.7rem;
        }}
        .badge-danger {{ background: var(--danger-bg); color: var(--danger); }}
        .badge-warning {{ background: var(--warning-bg); color: var(--warning); }}
        .badge-success {{ background: var(--success-bg); color: var(--success); }}
        .badge-primary {{ background: var(--primary-light); color: var(--primary); }}

        /* TABS NAVIGATION (ROUNDED-SM) */
        .tab-bar {{
            display: flex;
            gap: 6px;
            border-bottom: 2px solid var(--border-color);
            margin-bottom: 20px;
            overflow-x: auto;
            padding-bottom: 2px;
            -webkit-overflow-scrolling: touch;
        }}

        .tab-button {{
            background: transparent;
            border: none;
            font-family: inherit;
            font-size: 0.86rem;
            font-weight: 600;
            color: var(--text-muted);
            padding: 8px 14px;
            cursor: pointer;
            border-radius: var(--radius-sm) var(--radius-sm) 0 0;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            white-space: nowrap;
            transition: all 0.2s ease;
            position: relative;
        }}

        .tab-button:hover {{
            color: var(--primary);
            background: var(--bg-card-subtle);
        }}

        .tab-button.active {{
            color: var(--primary);
            background: var(--bg-card);
        }}

        .tab-button.active::after {{
            content: '';
            position: absolute;
            bottom: -3px;
            left: 0;
            width: 100%;
            height: 3px;
            background: var(--primary);
            border-radius: var(--radius-sm) var(--radius-sm) 0 0;
        }}

        /* Tab Panes */
        .tab-view {{
            display: none;
        }}
        .tab-view.active {{
            display: block;
            animation: fadeIn 0.25s ease;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(4px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Charts Layout */
        .charts-grid-2 {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(min(100%, 460px), 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }}

        .chart-box {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            padding: 16px 18px;
            box-shadow: var(--shadow-xs);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}

        .chart-head {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            gap: 8px;
            flex-wrap: wrap;
        }}

        .chart-heading {{
            font-size: 0.92rem;
            font-weight: 700;
            color: var(--text-main);
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .chart-subheading {{
            font-size: 0.74rem;
            color: var(--text-muted);
        }}

        .chart-canvas-wrap {{
            position: relative;
            height: 290px;
            width: 100%;
        }}

        /* Callout Alert Box (rounded-sm) */
        .info-callout {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-left: 4px solid var(--primary);
            border-radius: var(--radius-sm);
            padding: 12px 16px;
            margin-bottom: 18px;
            box-shadow: var(--shadow-xs);
        }}
        .info-callout.danger {{ border-left-color: var(--danger); }}
        .info-callout.warning {{ border-left-color: var(--warning); }}

        .info-callout-title {{
            font-size: 0.88rem;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 4px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .info-callout.danger .info-callout-title {{ color: var(--danger); }}
        .info-callout.warning .info-callout-title {{ color: var(--warning); }}

        .info-callout-content {{
            font-size: 0.82rem;
            color: var(--text-muted);
            line-height: 1.55;
        }}

        /* Table Styling (rounded-sm) */
        .table-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            overflow: hidden;
            box-shadow: var(--shadow-xs);
        }}

        .table-toolbar {{
            padding: 10px 14px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }}

        .table-scroll {{
            overflow-x: auto;
            max-height: 480px;
        }}

        table.is-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.82rem;
            text-align: left;
        }}

        table.is-table th {{
            background: var(--bg-card-subtle);
            color: var(--text-main);
            padding: 8px 12px;
            font-weight: 600;
            border-bottom: 1px solid var(--border-color);
            position: sticky;
            top: 0;
            z-index: 2;
        }}

        table.is-table td {{
            padding: 8px 12px;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-main);
        }}

        table.is-table tr:hover td {{
            background: var(--bg-card-subtle);
        }}

        /* THAILAND SVG MAP STYLES */
        .map-section-wrapper {{
            display: grid;
            grid-template-columns: minmax(320px, 480px) 1fr;
            gap: 16px;
            margin-bottom: 20px;
        }}

        @media (max-width: 960px) {{
            .map-section-wrapper {{
                grid-template-columns: 1fr;
            }}
        }}

        .map-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            padding: 16px;
            display: flex;
            flex-direction: column;
            box-shadow: var(--shadow-xs);
            position: relative;
        }}

        .map-svg-container {{
            width: 100%;
            height: 600px;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
        }}

        svg.thailand-map-svg {{
            width: 100%;
            height: 100%;
            max-height: 580px;
            overflow: visible;
        }}

        .prov-path {{
            stroke: var(--border-color);
            stroke-width: 0.75;
            transition: all 0.2s ease;
            cursor: pointer;
        }}

        .prov-path:hover {{
            stroke: #ffffff;
            stroke-width: 2.5;
            filter: drop-shadow(0 0 6px rgba(2, 132, 199, 0.8));
        }}

        .prov-path.selected {{
            stroke: var(--warning);
            stroke-width: 3;
            filter: drop-shadow(0 0 8px rgba(245, 158, 11, 0.9));
        }}

        /* Map Floating Tooltip */
        .map-tooltip {{
            position: absolute;
            display: none;
            background: rgba(15, 23, 42, 0.95);
            color: #ffffff;
            padding: 8px 12px;
            border-radius: var(--radius-sm);
            font-size: 0.78rem;
            pointer-events: none;
            z-index: 100;
            box-shadow: var(--shadow-md);
            border: 1px solid rgba(255, 255, 255, 0.15);
            line-height: 1.4;
        }}

        /* Map Legend */
        .map-legend {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.72rem;
            color: var(--text-muted);
            margin-top: 10px;
            padding-top: 8px;
            border-top: 1px solid var(--border-color);
        }}

        .legend-gradient {{
            height: 8px;
            flex: 1;
            margin: 0 10px;
            border-radius: var(--radius-sm);
            background: linear-gradient(90deg, #93c5fd, #38bdf8, #f59e0b, #ef4444, #991b1b);
        }}

        /* Regional Summary Cards */
        .regions-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 8px;
            margin-bottom: 14px;
        }}

        .region-card {{
            background: var(--bg-card-subtle);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            padding: 8px 10px;
            text-align: center;
        }}
        .region-name {{ font-size: 0.72rem; font-weight: 600; color: var(--text-muted); }}
        .region-val {{ font-size: 0.98rem; font-weight: 700; color: var(--text-main); margin-top: 2px; }}

        /* MODAL STYLES (ROUNDED-SM) */
        .modal-mask {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.65);
            backdrop-filter: blur(4px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 2000;
            padding: 16px;
        }}

        .modal-mask.open {{
            display: flex;
        }}

        .modal-dialog {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            width: 100%;
            max-width: 620px;
            padding: 22px;
            box-shadow: var(--shadow-lg);
            animation: modalIn 0.2s ease;
        }}

        @keyframes modalIn {{
            from {{ transform: scale(0.96); opacity: 0; }}
            to {{ transform: scale(1); opacity: 1; }}
        }}

        .dropzone-box {{
            border: 2px dashed var(--primary);
            border-radius: var(--radius-sm);
            background: var(--bg-card-subtle);
            padding: 28px 16px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s ease;
            margin: 14px 0;
        }}

        .dropzone-box:hover {{
            background: var(--primary-light);
            border-color: var(--primary-dark);
        }}

        .dropzone-box i {{
            font-size: 2.4rem;
            color: var(--primary);
            margin-bottom: 8px;
        }}

        /* FOOTER (ACADEMIC & CITATION STANDARDS) */
        footer.dashboard-footer {{
            background: var(--bg-card);
            border-top: 1px solid var(--border-color);
            padding: 26px clamp(16px, 2.5vw, 28px);
            margin-top: 36px;
            color: var(--text-muted);
            font-size: 0.82rem;
        }}

        .footer-inner {{
            max-width: 1560px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        }}

        .footer-col h4 {{
            font-size: 0.9rem;
            font-weight: 700;
            color: var(--text-main);
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .footer-link {{
            color: var(--primary);
            text-decoration: none;
            font-weight: 600;
            word-break: break-all;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: color 0.2s;
        }}
        .footer-link:hover {{
            color: var(--primary-dark);
            text-decoration: underline;
        }}

        .footer-bottom {{
            max-width: 1560px;
            margin: 18px auto 0 auto;
            padding-top: 14px;
            border-top: 1px dashed var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 12px;
            font-size: 0.76rem;
        }}

        /* Print Media Styles */
        @media print {{
            body {{
                background: #ffffff !important;
                color: #000000 !important;
            }}
            .sticky-navbar, .filter-panel, .tab-bar, .theme-toggle-btn {{
                display: none !important;
            }}
            .tab-view {{
                display: block !important;
            }}
            .chart-box, .map-card {{
                break-inside: avoid;
                box-shadow: none !important;
                border: 1px solid #ccc !important;
                margin-bottom: 14px;
            }}
        }}
    </style>
</head>
<body>

<!-- 1. STICKY / FIXED TOPBAR & NAVBAR (RESPONSIVE) -->
<header class="sticky-navbar">
    <div class="navbar-container">
        <div class="brand-cluster">
            <div class="brand-badge-icon">
                <i class="fa-solid fa-heart-pulse"></i>
            </div>
            <div class="brand-meta">
                <h1>
                    ระบบเฝ้าระวังการบาดเจ็บแห่งชาติ (Injury Surveillance : IS)
                    <span class="badge-academic" id="dynamicAcademicBadge">
                        <i class="fa-solid fa-graduation-cap"></i> รายงานวิชาการ ประจำปี พ.ศ. 2569 (ค.ศ. 2026)
                    </span>
                </h1>
                <p><i class="fa-solid fa-hospital"></i> กรมควบคุมโรค กระทรวงสาธารณสุข | ฐานข้อมูลเวชระเบียนผู้บาดเจ็บระดับชาติ</p>
            </div>
        </div>

        <div class="navbar-actions">
            <button class="btn btn-primary" onclick="openImportModal()">
                <i class="fa-solid fa-file-arrow-up"></i> นำเข้าไฟล์ CSV
            </button>
            <button class="btn btn-danger-outline" onclick="confirmClearDataToZero()" title="ล้างข้อมูล">
                <i class="fa-solid fa-trash-can"></i> ล้างข้อมูล
            </button>
            <button class="btn btn-success-outline" onclick="loadSampleData()" title="โหลดข้อมูลตัวอย่าง">
                <i class="fa-solid fa-cloud-arrow-down"></i> โหลดข้อมูลตัวอย่าง
            </button>
            <button class="btn btn-outline" onclick="window.print()" title="พิมพ์รายงาน">
                <i class="fa-solid fa-print"></i> พิมพ์รายงาน
            </button>
            <button class="theme-toggle-btn" id="themeToggle" onclick="toggleTheme()" title="เปลี่ยนธีม สว่าง/มืด">
                <i class="fa-solid fa-moon"></i>
            </button>
        </div>
    </div>
</header>

<div class="container">
    <!-- REAL-TIME SEARCHABLE FILTER PANEL (DYNAMIC YEARS & TEMPORAL) -->
    <section class="filter-panel">
        <div class="filter-header">
            <div class="filter-title">
                <i class="fa-solid fa-filter" style="color:var(--primary);"></i> ตัวกรองข้อมูล (Filters)
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
                <span class="filter-stats-badge" id="filterStatusBadge">
                    <i class="fa-solid fa-circle-notch fa-spin"></i> กำลังโหลดฐานข้อมูล...
                </span>
                <button class="btn btn-outline" style="padding:3px 8px; font-size:0.76rem; min-height:28px;" onclick="resetAllFilters()">
                    <i class="fa-solid fa-arrow-rotate-left"></i> ล้างตัวกรอง
                </button>
            </div>
        </div>

        <div class="filter-grid">
            <!-- 1. Searchable Province -->
            <div class="filter-group">
                <label class="filter-label"><i class="fa-solid fa-location-dot"></i> ค้นหาจังหวัด</label>
                <input list="provinceList" id="filterProvInput" class="filter-input" placeholder="พิมพ์ชื่อจังหวัด..." oninput="onFilterChange()">
                <datalist id="provinceList">
                    <!-- Populated by JS -->
                </datalist>
            </div>

            <!-- 2. Dynamic Year Filter (ตรวจจับปีอัตโนมัติ) -->
            <div class="filter-group">
                <label class="filter-label"><i class="fa-solid fa-calendar"></i> ปีข้อมูล (Year)</label>
                <select id="filterYear" class="filter-select" onchange="onFilterChange()">
                    <option value="0">ทุกปีที่นำเข้า (All Years)</option>
                    <!-- Populated dynamically by JS -->
                </select>
            </div>

            <!-- 3. Temporal / Month Filter (ช่วงเวลา/เดือน) -->
            <div class="filter-group">
                <label class="filter-label"><i class="fa-solid fa-clock"></i> ช่วงเวลา/เดือน (Period)</label>
                <select id="filterPeriod" class="filter-select" onchange="onFilterChange()">
                    <option value="0">ทุกช่วงเดือน (All Months)</option>
                    <option value="Q1">ไตรมาส 1 (ม.ค. - มี.ค.)</option>
                    <option value="Q2">ไตรมาส 2 (เม.ย. - มิ.ย.)</option>
                    <option value="Q3">ไตรมาส 3 (ก.ค. - ก.ย.)</option>
                    <option value="Q4">ไตรมาส 4 (ต.ค. - ธ.ค.)</option>
                    <option value="1">มกราคม (Jan)</option>
                    <option value="2">กุมภาพันธ์ (Feb)</option>
                    <option value="3">มีนาคม (Mar)</option>
                    <option value="4">เมษายน (Apr)</option>
                    <option value="5">พฤษภาคม (May)</option>
                    <option value="6">มิถุนายน (Jun)</option>
                    <option value="7">กรกฎาคม (Jul)</option>
                    <option value="8">สิงหาคม (Aug)</option>
                    <option value="9">กันยายน (Sep)</option>
                    <option value="10">ตุลาคม (Oct)</option>
                    <option value="11">พฤศจิกายน (Nov)</option>
                    <option value="12">ธันวาคม (Dec)</option>
                </select>
            </div>

            <!-- 4. Gender -->
            <div class="filter-group">
                <label class="filter-label"><i class="fa-solid fa-venus-mars"></i> เพศ (Sex)</label>
                <select id="filterSex" class="filter-select" onchange="onFilterChange()">
                    <option value="0">ทั้งหมด (All)</option>
                    <option value="1">ชาย (Male)</option>
                    <option value="2">หญิง (Female)</option>
                </select>
            </div>

            <!-- 5. Age Group -->
            <div class="filter-group">
                <label class="filter-label"><i class="fa-solid fa-users"></i> กลุ่มอายุ (Age Group)</label>
                <select id="filterAge" class="filter-select" onchange="onFilterChange()">
                    <option value="0">ทั้งหมด (All Ages)</option>
                    <option value="1">0-14 ปี (เด็ก)</option>
                    <option value="2">15-24 ปี (เยาวชน)</option>
                    <option value="3">25-59 ปี (วัยทำงาน)</option>
                    <option value="4">60+ ปี (สูงอายุ)</option>
                </select>
            </div>

            <!-- 6. Vehicle -->
            <div class="filter-group">
                <label class="filter-label"><i class="fa-solid fa-motorcycle"></i> ยานพาหนะ (Vehicle)</label>
                <select id="filterVehicle" class="filter-select" onchange="onFilterChange()">
                    <option value="-1">ทั้งหมด (All Vehicles)</option>
                    <option value="1">รถจักรยานยนต์ (Motorcycle)</option>
                    <option value="2">รถเก๋ง / SUV</option>
                    <option value="3">รถปิคอัพ (Pickup)</option>
                    <option value="4">รถจักรยาน (Bicycle)</option>
                    <option value="5">รถบรรทุก / พ่วง</option>
                    <option value="6">รถโดยสาร / รถตู้</option>
                    <option value="7">แท็กซี่ / สามล้อ</option>
                    <option value="0">อื่นๆ / ไม่ระบุ</option>
                </select>
            </div>

            <!-- 7. Season / Holiday -->
            <div class="filter-group">
                <label class="filter-label"><i class="fa-solid fa-calendar-star"></i> เทศกาลสำคัญ (Holiday)</label>
                <select id="filterHoliday" class="filter-select" onchange="onFilterChange()">
                    <option value="0">ทุกช่วงเวลา (All Times)</option>
                    <option value="1">7 วันอันตรายปีใหม่ (1-7 ม.ค.)</option>
                    <option value="2">7 วันอันตรายสงกรานต์ (11-17 เม.ย.)</option>
                </select>
            </div>

            <!-- 8. Risk Factor & Severity -->
            <div class="filter-group">
                <label class="filter-label"><i class="fa-solid fa-triangle-exclamation"></i> ปัจจัยเสี่ยง & ผลลัพธ์</label>
                <select id="filterRisk" class="filter-select" onchange="onFilterChange()">
                    <option value="0">ทั้งหมด (All Records)</option>
                    <option value="alcohol">ดื่มแอลกอฮอล์ (Alcohol Risk)</option>
                    <option value="no_helmet">ไม่สวมหมวกนิรภัย (No Helmet)</option>
                    <option value="head_inj">บาดเจ็บศีรษะ (Head Injury)</option>
                    <option value="death">เสียชีวิต (Fatalities)</option>
                    <option value="admit">รับไว้รักษาใน รพ. (Admitted)</option>
                </select>
            </div>
        </div>

        <!-- Active Filter Chips -->
        <div class="filter-chips-bar" id="filterChipsBar" style="display:none;">
            <span class="chip-label">ตัวกรองที่ใช้งานอยู่:</span>
            <div id="chipsContainer" style="display:flex; flex-wrap:wrap; gap:6px;"></div>
        </div>
    </section>

    <!-- 6 EXECUTIVE KPI CARDS -->
    <section class="kpi-grid">
        <!-- 1. Total Cases -->
        <div class="kpi-card">
            <div class="kpi-top">
                <span class="kpi-label">ผู้บาดเจ็บสะสมรวม</span>
                <div class="kpi-icon-wrap"><i class="fa-solid fa-users"></i></div>
            </div>
            <div class="kpi-number" id="kpiCases">0</div>
            <div class="kpi-footer">
                <span id="kpiCasesSub">ชาย 0.0% | หญิง 0.0%</span>
            </div>
        </div>

        <!-- 2. Fatalities -->
        <div class="kpi-card danger">
            <div class="kpi-top">
                <span class="kpi-label">ผู้เสียชีวิตสะสม (Fatalities)</span>
                <div class="kpi-icon-wrap"><i class="fa-solid fa-skull-crossbones"></i></div>
            </div>
            <div class="kpi-number" id="kpiDeaths">0</div>
            <div class="kpi-footer">
                <span class="badge-pill badge-danger" id="kpiCFR">CFR 0.00%</span>
                <span id="kpiDeathsSub">ER 0 | Ward 0</span>
            </div>
        </div>

        <!-- 3. Hospital Admits -->
        <div class="kpi-card warning">
            <div class="kpi-top">
                <span class="kpi-label">รับไว้รักษาใน รพ. (Admit)</span>
                <div class="kpi-icon-wrap"><i class="fa-solid fa-bed-pulse"></i></div>
            </div>
            <div class="kpi-number" id="kpiAdmits">0</div>
            <div class="kpi-footer">
                <span class="badge-pill badge-warning" id="kpiAdmitRate">0.0%</span>
                <span>ต้องนอนโรงพยาบาล</span>
            </div>
        </div>

        <!-- 4. Head Injury -->
        <div class="kpi-card danger">
            <div class="kpi-top">
                <span class="kpi-label">บาดเจ็บรุนแรงที่ศีรษะ (HI)</span>
                <div class="kpi-icon-wrap"><i class="fa-solid fa-brain"></i></div>
            </div>
            <div class="kpi-number" id="kpiHeadInj">0</div>
            <div class="kpi-footer">
                <span class="badge-pill badge-danger" id="kpiHIRate">0.0%</span>
                <span>ของเคสบาดเจ็บ</span>
            </div>
        </div>

        <!-- 5. Motorcycle Cases -->
        <div class="kpi-card accent">
            <div class="kpi-top">
                <span class="kpi-label">รถจักรยานยนต์ (จยย.)</span>
                <div class="kpi-icon-wrap"><i class="fa-solid fa-motorcycle"></i></div>
            </div>
            <div class="kpi-number" id="kpiMotos">0</div>
            <div class="kpi-footer">
                <span class="badge-pill badge-primary" id="kpiMotoRate">0.0%</span>
                <span>ของยานพาหนะทั้งหมด</span>
            </div>
        </div>

        <!-- 6. No Helmet Rate -->
        <div class="kpi-card danger">
            <div class="kpi-top">
                <span class="kpi-label">จยย. ไม่สวมหมวกนิรภัย</span>
                <div class="kpi-icon-wrap"><i class="fa-solid fa-helmet-un"></i></div>
            </div>
            <div class="kpi-number" id="kpiNoHelmet">0</div>
            <div class="kpi-footer">
                <span class="badge-pill badge-danger" id="kpiNoHelmetRate">0.0%</span>
                <span>ของผู้บาดเจ็บจาก จยย.</span>
            </div>
        </div>
    </section>

    <!-- NAVIGATION TAB BAR -->
    <nav class="tab-bar">
        <button class="tab-button active" onclick="activateTab('epidemiology')">
            <i class="fa-solid fa-chart-pie"></i> ภาพรวมระบาดวิทยา
        </button>
        <button class="tab-button" onclick="activateTab('risks')">
            <i class="fa-solid fa-motorcycle"></i> ยานพาหนะ & พฤติกรรมเสี่ยง
        </button>
        <button class="tab-button" onclick="activateTab('temporal')">
            <i class="fa-solid fa-calendar-week"></i> มิติเวลา & เทศกาลอันตราย
        </button>
        <button class="tab-button" onclick="activateTab('provinces')">
            <i class="fa-solid fa-map-location-dot"></i> แผนที่ 77 จังหวัด & เชิงพื้นที่
        </button>
        <button class="tab-button" onclick="activateTab('clinical')">
            <i class="fa-solid fa-truck-medical"></i> EMS & ผลการรักษา
        </button>
        <button class="tab-button" onclick="activateTab('academic')">
            <i class="fa-solid fa-book-bookmark"></i> สรุปวิชาการ & นโยบาย
        </button>
    </nav>

    <!-- TAB 1: ภาพรวมระบาดวิทยา -->
    <div id="view-epidemiology" class="tab-view active">
        <div class="info-callout">
            <div class="info-callout-title">
                <i class="fa-solid fa-circle-info"></i> สรุปวิเคราะห์ทางระบาดวิทยา (Epidemiological Overview)
            </div>
            <div class="info-callout-content" id="overviewCalloutText">
                ระบบเฝ้าระวังการบาดเจ็บประมวลผลข้อมูลผู้ประสบอุบัติเหตุเพื่อการวิเคราะห์กลุ่มประชากรเปราะบาง สัดส่วนเพศ และอัตราการเสียชีวิต (Case Fatality Rate)
            </div>
        </div>

        <div class="charts-grid-2">
            <div class="chart-box">
                <div class="chart-head">
                    <div>
                        <div class="chart-heading"><i class="fa-solid fa-users" style="color:var(--primary);"></i> การกระจายตามกลุ่มอายุ (Age Pyramid)</div>
                        <div class="chart-subheading">จำแนกตามช่วงวัยของผู้บาดเจ็บ</div>
                    </div>
                </div>
                <div class="chart-canvas-wrap">
                    <canvas id="chartAge"></canvas>
                </div>
            </div>

            <div class="chart-box">
                <div class="chart-head">
                    <div>
                        <div class="chart-heading"><i class="fa-solid fa-venus-mars" style="color:var(--accent);"></i> สัดส่วนเพศและผลการรักษา</div>
                        <div class="chart-subheading">เปรียบเทียบการรักษาผู้บาดเจ็บชาย vs หญิง</div>
                    </div>
                </div>
                <div class="chart-canvas-wrap">
                    <canvas id="chartGender"></canvas>
                </div>
            </div>
        </div>
    </div>

    <!-- TAB 2: ยานพาหนะ & พฤติกรรมเสี่ยง -->
    <div id="view-risks" class="tab-view">
        <div class="info-callout danger">
            <div class="info-callout-title">
                <i class="fa-solid fa-brain"></i> ดัชนีความเสี่ยงสัมพัทธ์ (Relative Risk Analysis): หมวกนิรภัยกับภาวะบาดเจ็บศีรษะ
            </div>
            <div class="info-callout-content" id="relativeRiskContent">
                ผู้ขับขี่และโดยสารรถจักรยานยนต์ที่ไม่สวมหมวกนิรภัย มีโอกาสเกิดการบาดเจ็บที่ศีรษะ (Head Injury) สูงกว่ากลุ่มที่สวมหมวกอย่างมีนัยสำคัญ
            </div>
        </div>

        <div class="charts-grid-2">
            <div class="chart-box">
                <div class="chart-head">
                    <div>
                        <div class="chart-heading"><i class="fa-solid fa-car-burst" style="color:var(--danger);"></i> การกระจายตามประเภทยานพาหนะ</div>
                        <div class="chart-subheading">สัดส่วนยานพาหนะที่ประสบเหตุ</div>
                    </div>
                </div>
                <div class="chart-canvas-wrap">
                    <canvas id="chartVehicles"></canvas>
                </div>
            </div>

            <div class="chart-box">
                <div class="chart-head">
                    <div>
                        <div class="chart-heading"><i class="fa-solid fa-shield-halved" style="color:var(--success);"></i> ผลของการสวมหมวกนิรภัยต่อ Head Injury</div>
                        <div class="chart-subheading">สวมหมวก vs ไม่สวมหมวก (Cross-tabulation)</div>
                    </div>
                </div>
                <div class="chart-canvas-wrap">
                    <canvas id="chartHelmet"></canvas>
                </div>
            </div>
        </div>

        <div class="charts-grid-2">
            <div class="chart-box">
                <div class="chart-head">
                    <div>
                        <div class="chart-heading"><i class="fa-solid fa-wine-glass" style="color:var(--warning);"></i> การดื่มแอลกอฮอล์แยกตามช่วงวัย</div>
                        <div class="chart-subheading">สัดส่วนผู้บาดเจ็บที่ดื่มสุรา (Risk 1)</div>
                    </div>
                </div>
                <div class="chart-canvas-wrap">
                    <canvas id="chartAlcohol"></canvas>
                </div>
            </div>

            <div class="chart-box">
                <div class="chart-head">
                    <div>
                        <div class="chart-heading"><i class="fa-solid fa-person-walking" style="color:var(--primary);"></i> บทบาทของผู้ประสบเหตุบนท้องถนน</div>
                        <div class="chart-subheading">ผู้ขับขี่, ผู้โดยสาร และคนเดินเท้า</div>
                    </div>
                </div>
                <div class="chart-canvas-wrap">
                    <canvas id="chartUserTypes"></canvas>
                </div>
            </div>
        </div>
    </div>

    <!-- TAB 3: มิติเวลา & เทศกาลอันตราย -->
    <div id="view-temporal" class="tab-view">
        <div class="info-callout warning">
            <div class="info-callout-title">
                <i class="fa-solid fa-fire"></i> พลวัตเวลาและเทศกาลวันหยุดยาว (Temporal & Peak Seasons)
            </div>
            <div class="info-callout-content" id="temporalCalloutText">
                สถิติการเกิดเหตุตามช่วงเวลาของวันและเทศกาลวันหยุด 7 วันอันตราย
            </div>
        </div>

        <div class="charts-grid-2">
            <div class="chart-box">
                <div class="chart-head">
                    <div>
                        <div class="chart-heading"><i class="fa-solid fa-chart-line" style="color:var(--primary);"></i> แนวโน้มผู้บาดเจ็บตามเดือน/ปี</div>
                        <div class="chart-subheading">การกระจายตามช่วงเวลาที่เกิดเหตุ</div>
                    </div>
                </div>
                <div class="chart-canvas-wrap">
                    <canvas id="chartMonthly"></canvas>
                </div>
            </div>

            <div class="chart-box">
                <div class="chart-head">
                    <div>
                        <div class="chart-heading"><i class="fa-solid fa-calendar-days" style="color:var(--danger);"></i> ยอดผู้บาดเจ็บช่วง 7 วันอันตราย</div>
                        <div class="chart-subheading">เปรียบเทียบปีใหม่ vs สงกรานต์</div>
                    </div>
                </div>
                <div class="chart-canvas-wrap">
                    <canvas id="chartHolidays"></canvas>
                </div>
            </div>
        </div>

        <div class="chart-box" style="margin-bottom:20px;">
            <div class="chart-head">
                <div>
                    <div class="chart-heading"><i class="fa-solid fa-clock-rotate-left" style="color:var(--warning);"></i> การกระจายตามชั่วโมงในรอบวัน (Hourly Distribution: 0:00 - 23:00 น.)</div>
                    <div class="chart-subheading">แสดงความเสี่ยงตามช่วงเวลาการเดินทาง</div>
                </div>
            </div>
            <div class="chart-canvas-wrap" style="height:260px;">
                <canvas id="chartHourly"></canvas>
            </div>
        </div>
    </div>

    <!-- TAB 4: แผนที่ 77 จังหวัด & เชิงพื้นที่ (INTERACTIVE THAILAND MAP) -->
    <div id="view-provinces" class="tab-view">
        <div class="info-callout">
            <div class="info-callout-title">
                <i class="fa-solid fa-map-location-dot"></i> การวิเคราะห์เชิงพื้นที่และแผนที่ความรุนแรง 77 จังหวัด (Thailand Choropleth Map)
            </div>
            <div class="info-callout-content">
                ท่านสามารถเลื่อนเมาส์ไปบนจังหวัดเพื่อดูข้อมูลสถิติเฉพาะพื้นที่ หรือ<strong>คลิกที่จังหวัดบนแผนที่</strong> เพื่อกรองข้อมูลของจังหวัดนั้นแบบ Real-time ทั้ง Dashboard
            </div>
        </div>

        <!-- Regional Summary Bar -->
        <div class="regions-grid" id="regionsGrid">
            <!-- Populated by JS -->
        </div>

        <div class="map-section-wrapper">
            <!-- Left: Interactive Vector Map -->
            <div class="map-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <div style="font-weight:700; font-size:0.92rem; color:var(--text-main);">
                        <i class="fa-solid fa-map" style="color:var(--primary);"></i> แผนที่ความหนาแน่นผู้บาดเจ็บ
                    </div>
                    <button class="btn btn-outline" style="padding:2px 8px; font-size:0.74rem; min-height:26px;" onclick="resetProvinceSelection()">
                        <i class="fa-solid fa-rotate-left"></i> ล้างการเลือกจังหวัด
                    </button>
                </div>

                <div class="map-svg-container">
                    <svg id="thailandSvg" class="thailand-map-svg" viewBox="0 0 550 920">
                        <!-- Injected by JS from SVG Paths -->
                    </svg>
                    <!-- Floating Tooltip -->
                    <div id="mapTooltip" class="map-tooltip"></div>
                </div>

                <!-- Legend -->
                <div class="map-legend">
                    <span>น้อย (Low)</span>
                    <div class="legend-gradient"></div>
                    <span style="color:var(--danger); font-weight:700;">สูง (High)</span>
                </div>
            </div>

            <!-- Right: Top 15 Bar & Table -->
            <div style="display:flex; flex-direction:column; gap:16px;">
                <div class="chart-box">
                    <div class="chart-head">
                        <div>
                            <div class="chart-heading"><i class="fa-solid fa-ranking-star" style="color:var(--primary);"></i> 15 จังหวัดที่พบผู้บาดเจ็บสูงสุด</div>
                            <div class="chart-subheading">เรียงตามจำนวนผู้ประสบเหตุ</div>
                        </div>
                    </div>
                    <div class="chart-canvas-wrap" style="height:250px;">
                        <canvas id="chartTopProv"></canvas>
                    </div>
                </div>

                <div class="table-card">
                    <div class="table-toolbar">
                        <div style="font-weight:700; font-size:0.88rem; color:var(--text-main);">
                            <i class="fa-solid fa-table-list" style="color:var(--primary);"></i> สถิติข้อมูลจำแนกรายจังหวัด
                        </div>
                        <div>
                            <input type="text" id="provTableSearch" placeholder="🔍 ค้นหาในตาราง..." oninput="filterProvinceTable()" class="filter-input" style="width:160px; padding:3px 7px; font-size:0.78rem;">
                        </div>
                    </div>
                    <div class="table-scroll" style="max-height:280px;">
                        <table class="is-table" id="provTable">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>จังหวัด</th>
                                    <th style="text-align:right;">ผู้บาดเจ็บ</th>
                                    <th style="text-align:right;">เสียชีวิต</th>
                                    <th style="text-align:right;">Admit</th>
                                    <th style="text-align:right;">Head Inj</th>
                                </tr>
                            </thead>
                            <tbody id="provTableBody">
                                <!-- Populated by JS -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- TAB 5: EMS & ผลการรักษา -->
    <div id="view-clinical" class="tab-view">
        <div class="charts-grid-2">
            <div class="chart-box">
                <div class="chart-head">
                    <div>
                        <div class="chart-heading"><i class="fa-solid fa-ambulance" style="color:var(--primary);"></i> ระดับบริการการแพทย์ฉุกเฉิน (EMS)</div>
                        <div class="chart-subheading">FR, BLS, ALS, ILS และการนำส่ง</div>
                    </div>
                </div>
                <div class="chart-canvas-wrap">
                    <canvas id="chartEMS"></canvas>
                </div>
            </div>

            <div class="chart-box">
                <div class="chart-head">
                    <div>
                        <div class="chart-heading"><i class="fa-solid fa-hospital-user" style="color:var(--secondary);"></i> ผลการจำหน่ายจากห้องฉุกเฉิน (ER Status)</div>
                        <div class="chart-subheading">จำหน่ายกลับบ้าน, Admit, ส่งต่อ, เสียชีวิต</div>
                    </div>
                </div>
                <div class="chart-canvas-wrap">
                    <canvas id="chartER"></canvas>
                </div>
            </div>
        </div>
    </div>

    <!-- TAB 6: สรุปวิชาการ & นโยบาย -->
    <div id="view-academic" class="tab-view">
        <div class="chart-box" style="margin-bottom:20px; line-height:1.75;">
            <div class="chart-head">
                <div class="chart-heading" style="font-size:1.05rem; color:var(--primary);">
                    <i class="fa-solid fa-graduation-cap"></i> รายงานเชิงวิชาการและการประเมินความคุ้มค่าเชิงนโยบาย (Academic Report)
                </div>
            </div>
            
            <div style="font-size:0.86rem; color:var(--text-main);">
                <h3 style="margin-top:10px; margin-bottom:6px; color:var(--primary);">1. วัตถุประสงค์และการประมวลผลข้อมูล (Methodology & Objectives)</h3>
                <p style="color:var(--text-muted); margin-bottom:14px;" id="reportMethodologyText">
                    การศึกษานี้ใช้ข้อมูลจากระบบเฝ้าระวังการบาดเจ็บแห่งชาติ (Injury Surveillance: IS) กรมควบคุมโรค กระทรวงสาธารณสุข 
                    โดยประมวลผลภายใต้แนวทางพระราชบัญญัติคุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562 (PDPA) ในรูปแบบข้อมูลสถิติรวมที่ไม่มีการระบุตัวตนบุคคล (De-identified Aggregate Data)
                </p>

                <h3 style="margin-top:10px; margin-bottom:6px; color:var(--primary);">2. ข้อค้นพบหลักด้านระบาดวิทยา (Core Epidemiological Findings)</h3>
                <ul style="margin-left:20px; color:var(--text-muted); margin-bottom:14px;">
                    <li><strong>ยานพาหนะวิกฤติ:</strong> รถจักรยานยนต์มีสัดส่วนสูงที่สุดของการบาดเจ็บทางถนนทั้งหมดในประเทศไทย</li>
                    <li><strong>พฤติกรรมเสี่ยงหลัก:</strong> การไม่สวมหมวกนิรภัยในผู้ขับขี่และโดยสารจักรยานยนต์ เพิ่มความเสี่ยงต่อภาวะบาดเจ็บที่ศีรษะ (Relative Risk: RR > 3.0 เท่า)</li>
                    <li><strong>สูญเสียกำลังคนวัยแรงงาน:</strong> กลุ่มวัยทำงานและเยาวชนได้รับผลกระทบสูงสุด คิดเป็นสัดส่วนมากกว่าร้อยละ 70 ของผู้บาดเจ็บทั้งหมด</li>
                </ul>

                <h3 style="margin-top:10px; margin-bottom:6px; color:var(--primary);">3. ข้อเสนอแนะเชิงนโยบาย (Public Health Policy Recommendations)</h3>
                <ol style="margin-left:20px; color:var(--text-muted); margin-bottom:14px;">
                    <li><strong>มาตรการส่งเสริมหมวกนิรภัยมาตรฐาน:</strong> สนับสนุนการเข้าถึงหมวกนิรภัยที่ได้มาตรฐาน มอก. ในราคาประหยัดสำหรับเด็กและเยาวชน ควบคู่กับการกวดขันกฎหมายในพื้นที่อำเภอเสี่ยง</li>
                    <li><strong>การจัดระบบการแพทย์ฉุกเฉินเชิงรับจุดเสี่ยง (Dynamic EMS Dispatch):</strong> วางกำลังหน่วยกู้ชีพ FR และ BLS บนเส้นทางสายรองในช่วงเวลา 17.00 - 20.00 น. เพื่อลดระยะเวลา Response Time</li>
                    <li><strong>ด่านชุมชนและควบคุมแอลกอฮอล์:</strong> เพิ่มความเข้มงวดของด่านชุมชนในช่วงเทศกาลสงกรานต์และปีใหม่ เพื่อสกัดกั้นผู้ขับขี่ที่มีพฤติกรรมดื่มแล้วขับ</li>
                </ol>
            </div>
        </div>
    </div>
</div>

<!-- 3. ACADEMIC FOOTER WITH OFFICIAL CITATION & DATA SOURCE -->
<footer class="dashboard-footer">
    <div class="footer-inner">
        <!-- Col 1: Dataset Reference & Data.go.th Link -->
        <div class="footer-col">
            <h4><i class="fa-solid fa-database" style="color:var(--primary);"></i> แหล่งข้อมูลอ้างอิงหลัก (Open Government Data)</h4>
            <p style="margin-bottom:8px; line-height:1.6;">
                ข้อมูลระบบเฝ้าระวังการบาดเจ็บแห่งชาติ (Injury Surveillance: IS) โดย กรมควบคุมโรค กระทรวงสาธารณสุข
            </p>
            <p>
                <a class="footer-link" href="https://data.go.th/dataset/gdpublish-injury-surveillance-is" target="_blank" rel="noopener noreferrer">
                    <i class="fa-solid fa-up-right-from-square"></i> https://data.go.th/dataset/gdpublish-injury-surveillance-is
                </a>
            </p>
        </div>

        <!-- Col 2: Academic Citation Format -->
        <div class="footer-col">
            <h4><i class="fa-solid fa-book" style="color:var(--secondary);"></i> รูปแบบการอ้างอิงทางวิชาการ (Academic Citation)</h4>
            <p style="font-size:0.78rem; line-height:1.6; background:var(--bg-card-subtle); padding:10px; border-radius:var(--radius-sm); border:1px solid var(--border-color);" id="footerCitationText">
                กรมควบคุมโรค กระทรวงสาธารณสุข. <em>ฐานข้อมูลระบบเฝ้าระวังการบาดเจ็บ (Injury Surveillance: IS)</em>. ศูนย์กลางข้อมูลเปิดภาครัฐ (Open Data Thailand). สืบค้นจาก https://data.go.th/dataset/gdpublish-injury-surveillance-is
            </p>
        </div>

        <!-- Col 3: Standards & License -->
        <div class="footer-col">
            <h4><i class="fa-solid fa-shield-halved" style="color:var(--success);"></i> มาตรฐานการกำกับดูแลข้อมูล</h4>
            <ul style="list-style:none; line-height:1.8; font-size:0.78rem;">
                <li><i class="fa-solid fa-check" style="color:var(--success);"></i> สัญญาอนุญาต: Open Government License (OGL-TH)</li>
                <li><i class="fa-solid fa-check" style="color:var(--success);"></i> พ.ร.บ. คุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562 (PDPA)</li>
                <li><i class="fa-solid fa-check" style="color:var(--success);"></i> มาตรฐานรหัสโรคสากล: WHO ICD-10 (Chapter 20)</li>
            </ul>
        </div>
    </div>

    <div class="footer-bottom">
        <div>
            © รายงานวิเคราะห์ระบาดวิทยาและเวชระเบียนฉุกเฉิน (Injury Surveillance Dashboard)
        </div>
    </div>
</footer>

<!-- 2. ADVANCED MULTI-FILE IMPORT MODAL -->
<div class="modal-mask" id="importModal">
    <div class="modal-dialog">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <h3 style="font-size:1.02rem; font-weight:700; color:var(--text-main); display:flex; align-items:center; gap:8px;">
                <i class="fa-solid fa-file-csv" style="color:var(--primary);"></i> นำเข้าไฟล์ CSV (รองรับหลายไฟล์/หลายปีพร้อมกัน)
            </h3>
            <button onclick="closeImportModal()" style="background:none; border:none; font-size:1.2rem; cursor:pointer; color:var(--text-muted);">
                <i class="fa-solid fa-xmark"></i>
            </button>
        </div>
        <p style="font-size:0.8rem; color:var(--text-muted); line-height:1.5;">
            ท่านสามารถเลือกหรือลากไฟล์ CSV <strong>หลายไฟล์พร้อมกัน</strong> (เช่น <code>is2025.csv</code>, <code>is2026.csv</code>) ระบบมีกลไก <strong>Smart Fingerprint Deduplication</strong> ป้องกันข้อมูลซ้ำซ้อนอย่างแม่นยำ 100%
        </p>

        <div class="dropzone-box" id="dropzone" onclick="document.getElementById('csvFileInput').click()">
            <i class="fa-solid fa-cloud-arrow-up"></i>
            <div style="font-weight:700; font-size:0.92rem; color:var(--text-main);">คลิกเพื่อเลือกไฟล์ หรือลากไฟล์ CSV มาวางที่นี่</div>
            <div style="font-size:0.78rem; color:var(--text-muted); margin-top:4px;">(สามารถเลือกหลายไฟล์พร้อมกันได้ - กด Ctrl / Shift)</div>
            <input type="file" id="csvFileInput" accept=".csv" multiple style="display:none;" onchange="handleMultipleFileSelect(event)">
        </div>

        <div style="margin-bottom:14px; font-size:0.8rem;">
            <div style="font-weight:600; margin-bottom:6px; color:var(--text-main);">รูปแบบการรวมข้อมูล:</div>
            <label style="display:inline-flex; align-items:center; gap:6px; margin-right:16px; cursor:pointer;">
                <input type="radio" name="importMode" value="append" checked> รวมข้อมูลต่อท้ายพร้อมคัดกรองข้อมูลซ้ำ (Smart Deduplication)
            </label>
            <label style="display:inline-flex; align-items:center; gap:6px; cursor:pointer;">
                <input type="radio" name="importMode" value="replace"> ล้างข้อมูลเดิมและแทนที่ด้วยชุดใหม่
            </label>
        </div>

        <div id="importProgressBar" style="display:none; margin-top:12px;">
            <div style="display:flex; justify-content:space-between; font-size:0.78rem; color:var(--text-muted);">
                <span id="importStatusText">กำลังประมวลผล...</span>
                <span id="importPct">0%</span>
            </div>
            <div style="height:6px; background:var(--border-color); border-radius:var(--radius-sm); overflow:hidden; margin-top:6px;">
                <div id="importFill" style="height:100%; width:0%; background:var(--primary); transition:width 0.2s;"></div>
            </div>
        </div>

        <div id="importStatsLog" style="display:none; font-size:0.8rem; padding:10px; background:var(--bg-card-subtle); border-radius:var(--radius-sm); margin-top:12px; border:1px solid var(--border-color);">
            <!-- Populated after import -->
        </div>

        <div style="margin-top:16px; display:flex; justify-content:space-between; align-items:center;">
            <button class="btn btn-danger-outline" onclick="confirmClearDataToZero()">
                <i class="fa-solid fa-trash-can"></i> ล้างข้อมูล
            </button>
            <button class="btn btn-outline" onclick="closeImportModal()">ปิดหน้าต่าง</button>
        </div>
    </div>
</div>

<script>
    // Embedded Metadata, Master Precomputed Data, and Thailand Map SVG Paths
    let provincesList = {provinces_json};
    let yearsList = {years_json};
    const masterData = {stats_json};
    const b64Data = "{b64_data}";
    const svgMapPaths = {svg_paths_json};

    // Regional grouping for Thailand
    const REGION_MAP = {{
        'เหนือ': ['เชียงใหม่', 'เชียงราย', 'ลำปาง', 'ลำพูน', 'แม่ฮ่องสอน', 'น่าน', 'พะเยา', 'แพร่', 'อุตรดิตถ์'],
        'อีสาน': ['นครราชสีมา', 'ขอนแก่น', 'อุบลราชธานี', 'อุดรธานี', 'บุรีรัมย์', 'สุรินทร์', 'ศรีสะเกษ', 'ร้อยเอ็ด', 'สกลนคร', 'ชัยภูมิ', 'กาฬสินธุ์', 'มหาสารคาม', 'นครพนม', 'เลย', 'ยโสธร', 'หนองคาย', 'บึงกาฬ', 'หนองบัวลำภู', 'อำนาจเจริญ', 'มุกดาหาร'],
        'กลาง': ['กรุงเทพมหานคร', 'นนทบุรี', 'ปทุมธานี', 'สมุทรปราการ', 'พระนครศรีอยุธยา', 'สระบุรี', 'ลพบุรี', 'สิงห์บุรี', 'อ่างทอง', 'ชัยนาท', 'นครนายก', 'สุพรรณบุรี', 'นครปฐม', 'สมุทรสาคร', 'สมุทรสงคราม', 'นครสวรรค์', 'อุทัยธานี', 'กำแพงเพชร', 'พิจิตร', 'พิษณุโลก', 'เพชรบูรณ์', 'สุโขทัย'],
        'ตะวันออก': ['ชลบุรี', 'ระยอง', 'จันทบุรี', 'ตราด', 'ฉะเชิงเทรา', 'ปราจีนบุรี', 'สระแก้ว'],
        'ตะวันตก': ['กาญจนบุรี', 'ราชบุรี', 'เพชรบุรี', 'ประจวบคีรีขันธ์', 'ตาก'],
        'ใต้': ['สงขลา', 'สุราษฎร์ธานี', 'นครศรีธรรมราช', 'ภูเก็ต', 'กระบี่', 'ตรัง', 'พัทลุง', 'ชุมพร', 'พังงา', 'ระนอง', 'สตูล', 'ปัตตานี', 'ยะลา', 'นราธิวาส']
    }};

    // Global in-memory dataset state
    let defaultRawRecords = null;
    let currentRawRecords = null;
    let charts = {{}};
    let isDataLoaded = false;
    let selectedMapProvince = '';

    // Deduplication Fingerprint Store
    let deduplicationSet = new Set();
    let importedFileNames = [];

    // Filter criteria state
    const currentFilters = {{
        prov: '',
        year: '0',
        period: '0',
        sex: 0,
        age: 0,
        vehicle: -1,
        holiday: 0,
        risk: '0'
    }};

    const VEHICLE_NAMES = {{
        1: 'รถจักรยานยนต์', 2: 'รถเก๋ง / SUV', 3: 'รถปิคอัพ', 4: 'รถจักรยาน',
        5: 'รถบรรทุก / พ่วง', 6: 'รถโดยสาร / รถตู้', 7: 'แท็กซี่ / สามล้อ', 0: 'อื่นๆ / ไม่ระบุ'
    }};

    const MONTH_THAI = {{
        1: 'ม.ค.', 2: 'ก.พ.', 3: 'มี.ค.', 4: 'เม.ย.', 5: 'พ.ค.', 6: 'มิ.ย.',
        7: 'ก.ค.', 8: 'ส.ค.', 9: 'ก.ย.', 10: 'ต.ค.', 11: 'พ.ย.', 12: 'ธ.ค.'
    }};

    function fnum(n) {{
        return Number(n || 0).toLocaleString();
    }}

    function activateTab(tabName) {{
        document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-view').forEach(view => view.classList.remove('active'));
        
        const activeBtn = Array.from(document.querySelectorAll('.tab-button')).find(b => b.getAttribute('onclick').includes(tabName));
        if (activeBtn) activeBtn.classList.add('active');
        
        const activeView = document.getElementById('view-' + tabName);
        if (activeView) activeView.classList.add('active');
    }}

    function toggleTheme() {{
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        if (isDark) {{
            document.documentElement.removeAttribute('data-theme');
            document.getElementById('themeToggle').innerHTML = '<i class="fa-solid fa-moon"></i>';
            localStorage.setItem('is_theme', 'light');
        }} else {{
            document.documentElement.setAttribute('data-theme', 'dark');
            document.getElementById('themeToggle').innerHTML = '<i class="fa-solid fa-sun"></i>';
            localStorage.setItem('is_theme', 'dark');
        }}
        setTimeout(refreshChartsWithCurrentData, 50);
    }}

    function setupProvinceDatalist() {{
        const dl = document.getElementById('provinceList');
        dl.innerHTML = '';
        provincesList.forEach(p => {{
            const opt = document.createElement('option');
            opt.value = p;
            dl.appendChild(opt);
        }});
    }}

    // UNIVERSAL ROBUST DATE PARSER (SUPPORTS CE/BE, ISO, SLASH, DASH, HDATE FALLBACK)
    function parseISDate(dateStr) {{
        if (!dateStr) return null;
        const trimmed = String(dateStr).trim();
        if (!trimmed) return null;

        let datePart = trimmed;
        let timePart = '';
        
        if (trimmed.includes('T')) {{
            const parts = trimmed.split('T');
            datePart = parts[0];
            timePart = parts[1] || '';
        }} else if (trimmed.includes(' ')) {{
            const parts = trimmed.split(/\\s+/);
            datePart = parts[0];
            timePart = parts[1] || '';
        }}

        let day = 1, month = 1, year = 0;

        if (datePart.includes('/')) {{
            const parts = datePart.split('/');
            if (parts.length === 3) {{
                const p0 = parseInt(parts[0], 10);
                const p1 = parseInt(parts[1], 10);
                const p2 = parseInt(parts[2], 10);

                if (p0 > 1000) {{
                    // YYYY/MM/DD
                    year = p0; month = p1; day = p2;
                }} else if (p2 > 1000) {{
                    year = p2;
                    if (p0 > 12) {{
                        day = p0; month = p1;
                    }} else if (p1 > 12) {{
                        month = p0; day = p1;
                    }} else {{
                        day = p0; month = p1;
                    }}
                }}
            }}
        }} else if (datePart.includes('-')) {{
            const parts = datePart.split('-');
            if (parts.length === 3) {{
                const p0 = parseInt(parts[0], 10);
                const p1 = parseInt(parts[1], 10);
                const p2 = parseInt(parts[2], 10);

                if (p0 > 1000) {{
                    // YYYY-MM-DD
                    year = p0; month = p1; day = p2;
                }} else if (p2 > 1000) {{
                    // DD-MM-YYYY
                    year = p2; month = p1; day = p0;
                }}
            }}
        }}

        if (!year || isNaN(year)) return null;

        let hour = 0;
        if (timePart && timePart.includes(':')) {{
            const h = parseInt(timePart.split(':')[0], 10);
            if (!isNaN(h) && h >= 0 && h < 24) hour = h;
        }}

        // Standardize: Convert Christian Era (CE e.g. 2018) to Buddhist Era (BE e.g. 2561)
        let yearBE = year;
        let yearCE = year;
        if (year >= 1900 && year < 2400) {{
            yearBE = year + 543;
            yearCE = year;
        }} else if (year >= 2400) {{
            yearBE = year;
            yearCE = year - 543;
        }}

        return {{
            day: Math.min(31, Math.max(1, day || 1)),
            month: Math.min(12, Math.max(1, month || 1)),
            yearBE: yearBE,
            yearCE: yearCE,
            yearStr: String(yearBE),
            hour: hour
        }};
    }}

    function setupYearSelector() {{
        const sel = document.getElementById('filterYear');
        const prevVal = sel.value;
        sel.innerHTML = '<option value="0">ทุกปีที่นำเข้า (All Years)</option>';
        
        // Sort years numerically ascending
        const sortedYears = [...new Set(yearsList)].sort((a,b) => parseInt(a, 10) - parseInt(b, 10));
        sortedYears.forEach(yrBE => {{
            const beNum = parseInt(yrBE, 10);
            const ceNum = beNum > 2400 ? beNum - 543 : beNum;
            const opt = document.createElement('option');
            opt.value = yrBE;
            opt.textContent = `พ.ศ. ${{yrBE}} (ค.ศ. ${{ceNum}})`;
            sel.appendChild(opt);
        }});
        if (yearsList.includes(prevVal)) sel.value = prevVal;
    }}

    // UPDATE DYNAMIC ACADEMIC BADGE & REPORT HEADER
    function updateDynamicAcademicTitle() {{
        const badge = document.getElementById('dynamicAcademicBadge');
        const citation = document.getElementById('footerCitationText');
        const methodology = document.getElementById('reportMethodologyText');

        if (!currentRawRecords || currentRawRecords.length === 0) {{
            badge.innerHTML = '<i class="fa-solid fa-graduation-cap"></i> รายงานวิชาการ (พร้อมนำเข้าข้อมูล)';
            if (citation) citation.innerHTML = `กรมควบคุมโรค กระทรวงสาธารณสุข. <em>ฐานข้อมูลระบบเฝ้าระวังการบาดเจ็บ (Injury Surveillance: IS)</em>. ศูนย์กลางข้อมูลเปิดภาครัฐ. สืบค้นจาก https://data.go.th/dataset/gdpublish-injury-surveillance-is`;
            if (methodology) methodology.textContent = `ระบบพร้อมสำหรับการนำเข้าชุดข้อมูลระบบเฝ้าระวังการบาดเจ็บแห่งชาติ (Injury Surveillance: IS) กรมควบคุมโรค กระทรวงสาธารณสุข เพื่อการวิเคราะห์ทางวิชาการ`;
            return;
        }}

        // Determine years in scope (either currently filtered single year or all imported years)
        const activeFilterYear = document.getElementById('filterYear') ? document.getElementById('filterYear').value : '0';
        let targetYears = [];
        if (activeFilterYear !== '0') {{
            targetYears = [activeFilterYear];
        }} else {{
            targetYears = [...new Set(yearsList)].sort((a,b) => parseInt(a, 10) - parseInt(b, 10));
        }}

        let yearText = '';
        let citationYears = '';
        if (targetYears.length === 1) {{
            const be = targetYears[0];
            const ce = parseInt(be, 10) > 2400 ? parseInt(be, 10) - 543 : be;
            yearText = `ประจำปี พ.ศ. ${{be}} (ค.ศ. ${{ce}})`;
            citationYears = `พ.ศ. ${{be}}`;
        }} else if (targetYears.length > 1) {{
            const minBE = targetYears[0];
            const maxBE = targetYears[targetYears.length - 1];
            const minCE = parseInt(minBE, 10) > 2400 ? parseInt(minBE, 10) - 543 : minBE;
            const maxCE = parseInt(maxBE, 10) > 2400 ? parseInt(maxBE, 10) - 543 : maxBE;
            yearText = `ช่วงปี พ.ศ. ${{minBE}} – ${{maxBE}} (ค.ศ. ${{minCE}} – ${{maxCE}})`;
            citationYears = `พ.ศ. ${{minBE}}–${{maxBE}}`;
        }} else {{
            yearText = `ประจำปี พ.ศ. 2569 (ค.ศ. 2026)`;
            citationYears = `พ.ศ. 2569`;
        }}

        badge.innerHTML = `<i class="fa-solid fa-graduation-cap"></i> รายงานวิชาการ ${{yearText}}`;
        if (citation) citation.innerHTML = `กรมควบคุมโรค กระทรวงสาธารณสุข. (${{citationYears}}). <em>ฐานข้อมูลระบบเฝ้าระวังการบาดเจ็บ (Injury Surveillance: IS)</em>. ศูนย์กลางข้อมูลเปิดภาครัฐ. สืบค้นจาก https://data.go.th/dataset/gdpublish-injury-surveillance-is`;
        if (methodology) methodology.textContent = `การศึกษานี้ใช้ข้อมูลจากระบบเฝ้าระวังการบาดเจ็บแห่งชาติ (Injury Surveillance: IS) กรมควบคุมโรค กระทรวงสาธารณสุข ${{yearText}} รวมทั้งสิ้น ${{fnum(currentRawRecords.length / 8)}} รายการ โดยประมวลผลภายใต้แนวทางพระราชบัญญัติคุ้มครองข้อมูลส่วนบุคคล พ.ศ. 2562 (PDPA) ในรูปแบบข้อมูลสถิติรวมที่ไม่มีการระบุตัวตนบุคคล`;
    }}

    function openImportModal() {{ document.getElementById('importModal').classList.add('open'); }}
    function closeImportModal() {{ document.getElementById('importModal').classList.remove('open'); }}

    // BUILD INTERACTIVE THAILAND SVG MAP
    function renderThailandSvgMap(provincesData) {{
        const svg = document.getElementById('thailandSvg');
        svg.innerHTML = '';

        // Calculate max cases for gradient
        let maxCases = 1;
        Object.values(provincesData || {{}}).forEach(d => {{
            if (d.cases > maxCases) maxCases = d.cases;
        }});

        const tooltip = document.getElementById('mapTooltip');

        for (const [thName, pathD] of Object.entries(svgMapPaths)) {{
            if (!pathD) continue;
            const pData = (provincesData && provincesData[thName]) ? provincesData[thName] : {{ cases: 0, deaths: 0, admits: 0, head_inj: 0 }};
            const ratio = pData.cases / maxCases;
            
            // Generate color heat: low = soft cyan, medium = amber, high = emergency red
            let fillColor = '#cbd5e1'; // empty default
            if (pData.cases > 0) {{
                if (ratio < 0.2) fillColor = '#7dd3fc';
                else if (ratio < 0.45) fillColor = '#38bdf8';
                else if (ratio < 0.7) fillColor = '#fbbf24';
                else if (ratio < 0.85) fillColor = '#f87171';
                else fillColor = '#ef4444';
            }}

            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute('d', pathD);
            path.setAttribute('id', 'map_prov_' + thName);
            path.setAttribute('class', 'prov-path' + (selectedMapProvince === thName ? ' selected' : ''));
            path.setAttribute('fill', fillColor);
            path.setAttribute('data-name', thName);

            // Hover tooltip
            path.addEventListener('mousemove', (e) => {{
                const cfr = pData.cases > 0 ? ((pData.deaths / pData.cases) * 100).toFixed(2) : '0.00';
                tooltip.style.display = 'block';
                tooltip.style.left = (e.offsetX + 15) + 'px';
                tooltip.style.top = (e.offsetY - 10) + 'px';
                tooltip.innerHTML = `
                    <div style="font-weight:700; color:var(--primary); font-size:0.85rem; margin-bottom:2px;">📍 จ.${{thName}}</div>
                    <div>ผู้บาดเจ็บ: <strong>${{fnum(pData.cases)}}</strong> ราย</div>
                    <div>เสียชีวิต: <strong style="color:var(--danger);">${{fnum(pData.deaths)}}</strong> (CFR ${{cfr}}%)</div>
                    <div>บาดเจ็บศีรษะ (HI): <strong>${{fnum(pData.head_inj)}}</strong></div>
                    <div>รับรักษา (Admit): <strong>${{fnum(pData.admits)}}</strong></div>
                    <div style="font-size:0.7rem; color:#94a3b8; margin-top:3px;">(คลิกเพื่อกรองข้อมูลทั้งหน้า)</div>
                `;
            }});

            path.addEventListener('mouseleave', () => {{
                tooltip.style.display = 'none';
            }});

            // Click to filter by province
            path.addEventListener('click', () => {{
                if (selectedMapProvince === thName) {{
                    resetProvinceSelection();
                }} else {{
                    selectedMapProvince = thName;
                    document.getElementById('filterProvInput').value = thName;
                    onFilterChange();
                }}
            }});

            svg.appendChild(path);
        }}
    }}

    function resetProvinceSelection() {{
        selectedMapProvince = '';
        document.getElementById('filterProvInput').value = '';
        onFilterChange();
    }}

    // Render Regional Summary
    function renderRegionalBreakdown(provData) {{
        const grid = document.getElementById('regionsGrid');
        grid.innerHTML = '';
        
        for (const [regionName, provs] of Object.entries(REGION_MAP)) {{
            let regCases = 0, regDeaths = 0;
            provs.forEach(p => {{
                if (provData && provData[p]) {{
                    regCases += provData[p].cases;
                    regDeaths += provData[p].deaths;
                }}
            }});

            const card = document.createElement('div');
            card.className = 'region-card';
            card.innerHTML = `
                <div class="region-name">ภาค${{regionName}}</div>
                <div class="region-val">${{fnum(regCases)}}</div>
                <div style="font-size:0.68rem; color:var(--text-muted); margin-top:2px;">ดับ ${{fnum(regDeaths)}}</div>
            `;
            grid.appendChild(card);
        }}
    }}

    // Initialize Base Binary Dataset
    function initBinaryDataset() {{
        try {{
            const binaryString = atob(b64Data);
            const len = binaryString.length;
            const bytes = new Uint8Array(len);
            for (let i = 0; i < len; i++) {{
                bytes[i] = binaryString.charCodeAt(i);
            }}

            defaultRawRecords = fflate.decompressSync(bytes);
            currentRawRecords = defaultRawRecords;
            isDataLoaded = true;
            document.getElementById('filterStatusBadge').innerHTML = 
                '<i class="fa-solid fa-circle-check" style="color:var(--success);"></i> ฐานข้อมูลพร้อมใช้งาน (266,914 เคส)';
            
            setupYearSelector();
            updateDynamicAcademicTitle();
        }} catch (e) {{
            console.error('Binary decompression failed:', e);
            document.getElementById('filterStatusBadge').innerHTML = 
                '<i class="fa-solid fa-circle-check" style="color:var(--success);"></i> ฐานข้อมูลพร้อมใช้งาน';
        }}
    }}

    // CLEAR DATA
    function confirmClearDataToZero() {{
        if (confirm('ยืนยันการล้างข้อมูลทั้งหมดหรือไม่?')) {{
            currentRawRecords = new Uint8Array(0);
            deduplicationSet.clear();
            importedFileNames = [];
            yearsList = [];
            
            document.getElementById('importStatsLog').style.display = 'none';
            document.getElementById('filterStatusBadge').innerHTML = 
                '<i class="fa-solid fa-circle" style="color:var(--text-muted);"></i> ฐานข้อมูลว่าง (0 รายการ) - พร้อมนำเข้าไฟล์ CSV';
            
            setupYearSelector();
            resetAllFilters();
            renderAllData(getEmptyZeroStats());
            updateDynamicAcademicTitle();
            closeImportModal();
        }}
    }}

    // LOAD SAMPLE DEMO DATA
    function loadSampleData() {{
        if (!defaultRawRecords) return;
        currentRawRecords = defaultRawRecords;
        deduplicationSet.clear();
        importedFileNames = ['is2026.csv'];
        yearsList = ['2569'];

        document.getElementById('filterStatusBadge').innerHTML = 
            '<i class="fa-solid fa-circle-check" style="color:var(--success);"></i> โหลดข้อมูลตัวอย่างสำเร็จ (266,914 รายการ)';

        setupYearSelector();
        resetAllFilters();
        renderAllData(masterData);
        updateDynamicAcademicTitle();
        alert('โหลดข้อมูลตัวอย่างสำเร็จ (266,914 รายการ)');
    }}

    function getEmptyZeroStats() {{
        return {{
            total_cases: 0, total_deaths: 0, total_admits: 0, total_head_injury: 0,
            total_moto_cases: 0, total_no_helmet_moto: 0,
            gender: {{ 'ชาย': 0, 'หญิง': 0 }},
            age_groups: {{ '0-14 ปี (เด็ก)': 0, '15-24 ปี (เยาวชน)': 0, '25-59 ปี (วัยทำงาน)': 0, '60+ ปี (สูงอายุ)': 0 }},
            vehicles: {{ 'รถจักรยานยนต์': 0, 'รถปิคอัพ': 0, 'รถเก๋ง / SUV': 0, 'รถจักรยาน': 0, 'รถบรรทุก / พ่วง': 0, 'รถโดยสาร / รถตู้': 0, 'แท็กซี่ / สามล้อ': 0, 'อื่นๆ / ไม่ระบุ': 0 }},
            user_types: {{ 'ผู้ขับขี่': 0, 'ผู้โดยสาร': 0, 'คนเดินเท้า': 0, 'อื่นๆ/ไม่ระบุ': 0 }},
            cross_helmet_head_injury: {{
                'ไม่สวมหมวก': {{ hi: 0, non_hi: 0 }},
                'สวมหมวก': {{ hi: 0, non_hi: 0 }},
                'ไม่ทราบ': {{ hi: 0, non_hi: 0 }}
            }},
            alcohol_by_age: {{}},
            monthly: {{}},
            daily_peaks: {{}},
            hourly: new Array(24).fill(0),
            provinces: {{}},
            ems: {{ 'FR (เบื้องต้น)': 0, 'BLS (พื้นฐาน)': 0, 'ALS (ขั้นสูง)': 0, 'ILS (ระดับกลาง)': 0, 'ไม่ใช้/มาเอง': 0 }},
            er_status: {{ 'จำหน่ายกลับบ้าน': 0, 'รับไว้รักษา (Admit)': 0, 'ส่งต่อไป รพ. อื่น': 0, 'ปฏิเสธการรักษา': 0, 'หนีกลับ': 0, 'เสียชีวิตใน ER': 0, 'เสียชีวิตก่อนถึง ER': 0 }}
        }};
    }}

    // REAL-TIME FILTER ENGINE
    function onFilterChange() {{
        currentFilters.prov = document.getElementById('filterProvInput').value.trim();
        currentFilters.year = document.getElementById('filterYear').value;
        currentFilters.period = document.getElementById('filterPeriod').value;
        currentFilters.sex = parseInt(document.getElementById('filterSex').value, 10);
        currentFilters.age = parseInt(document.getElementById('filterAge').value, 10);
        currentFilters.vehicle = parseInt(document.getElementById('filterVehicle').value, 10);
        currentFilters.holiday = parseInt(document.getElementById('filterHoliday').value, 10);
        currentFilters.risk = document.getElementById('filterRisk').value;

        selectedMapProvince = currentFilters.prov;

        updateFilterChips();
        updateDynamicAcademicTitle();
        executeFastFilter();
    }}

    function resetAllFilters() {{
        document.getElementById('filterProvInput').value = '';
        document.getElementById('filterYear').value = '0';
        document.getElementById('filterPeriod').value = '0';
        document.getElementById('filterSex').value = '0';
        document.getElementById('filterAge').value = '0';
        document.getElementById('filterVehicle').value = '-1';
        document.getElementById('filterHoliday').value = '0';
        document.getElementById('filterRisk').value = '0';
        selectedMapProvince = '';
        onFilterChange();
    }}

    function updateFilterChips() {{
        const container = document.getElementById('chipsContainer');
        const bar = document.getElementById('filterChipsBar');
        container.innerHTML = '';
        let count = 0;

        if (currentFilters.prov) {{
            addChip('จังหวัด: ' + currentFilters.prov, () => {{ document.getElementById('filterProvInput').value = ''; onFilterChange(); }});
            count++;
        }}
        if (currentFilters.year !== '0') {{
            addChip('ปี พ.ศ.: ' + currentFilters.year, () => {{ document.getElementById('filterYear').value = '0'; onFilterChange(); }});
            count++;
        }}
        if (currentFilters.period !== '0') {{
            const pTexts = {{ 'Q1': 'ไตรมาส 1', 'Q2': 'ไตรมาส 2', 'Q3': 'ไตรมาส 3', 'Q4': 'ไตรมาส 4' }};
            addChip('ช่วงเวลา: ' + (pTexts[currentFilters.period] || (MONTH_THAI[currentFilters.period] || currentFilters.period)), () => {{ document.getElementById('filterPeriod').value = '0'; onFilterChange(); }});
            count++;
        }}
        if (currentFilters.sex > 0) {{
            addChip('เพศ: ' + (currentFilters.sex === 1 ? 'ชาย' : 'หญิง'), () => {{ document.getElementById('filterSex').value = '0'; onFilterChange(); }});
            count++;
        }}
        if (currentFilters.age > 0) {{
            const ageTexts = {{1: '0-14 ปี (เด็ก)', 2: '15-24 ปี (เยาวชน)', 3: '25-59 ปี (วัยทำงาน)', 4: '60+ ปี (สูงอายุ)'}};
            addChip('อายุ: ' + ageTexts[currentFilters.age], () => {{ document.getElementById('filterAge').value = '0'; onFilterChange(); }});
            count++;
        }}
        if (currentFilters.vehicle >= 0) {{
            addChip('ยานพาหนะ: ' + VEHICLE_NAMES[currentFilters.vehicle], () => {{ document.getElementById('filterVehicle').value = '-1'; onFilterChange(); }});
            count++;
        }}
        if (currentFilters.holiday > 0) {{
            addChip(currentFilters.holiday === 1 ? 'เทศกาลปีใหม่' : 'เทศกาลสงกรานต์', () => {{ document.getElementById('filterHoliday').value = '0'; onFilterChange(); }});
            count++;
        }}
        if (currentFilters.risk !== '0') {{
            const rTexts = {{
                'alcohol': 'ดื่มแอลกอฮอล์', 'no_helmet': 'ไม่สวมหมวกนิรภัย',
                'head_inj': 'บาดเจ็บศีรษะ', 'death': 'เสียชีวิต', 'admit': 'รับไว้รักษา (Admit)'
            }};
            addChip(rTexts[currentFilters.risk] || currentFilters.risk, () => {{ document.getElementById('filterRisk').value = '0'; onFilterChange(); }});
            count++;
        }}

        bar.style.display = count > 0 ? 'flex' : 'none';
    }}

    function addChip(text, onRemove) {{
        const chip = document.createElement('span');
        chip.className = 'filter-chip';
        chip.innerHTML = `${{text}} <i class="fa-solid fa-xmark close-btn"></i>`;
        chip.querySelector('.close-btn').onclick = onRemove;
        document.getElementById('chipsContainer').appendChild(chip);
    }}

    // DYNAMIC FILTERING & RE-COMPUTATION OVER TYPED ARRAY
    let currentFilteredStats = null;

    function executeFastFilter() {{
        if (!isDataLoaded || !currentRawRecords) return;

        if (currentRawRecords.length === 0) {{
            currentFilteredStats = getEmptyZeroStats();
            renderAllData(currentFilteredStats);
            return;
        }}

        const isDefault = (!currentFilters.prov && currentFilters.year === '0' && currentFilters.period === '0' &&
                           currentFilters.sex === 0 && currentFilters.age === 0 && currentFilters.vehicle === -1 &&
                           currentFilters.holiday === 0 && currentFilters.risk === '0' &&
                           currentRawRecords === defaultRawRecords);

        if (isDefault) {{
            currentFilteredStats = masterData;
            renderAllData(masterData);
            return;
        }}

        let targetPid = -1;
        if (currentFilters.prov) {{
            targetPid = provincesList.indexOf(currentFilters.prov);
        }}

        const f_yr = currentFilters.year;
        const f_period = currentFilters.period;
        const f_sex = currentFilters.sex;
        const f_ag = currentFilters.age;
        const f_vid = currentFilters.vehicle;
        const f_hld = currentFilters.holiday;
        const f_risk = currentFilters.risk;

        let total = 0, deaths = 0, admits = 0, head_inj = 0;
        let motos = 0, no_helmet = 0, alc = 0;
        let sex_m = 0, sex_f = 0;
        
        const age_counts = [0, 0, 0, 0, 0];
        const v_counts = [0, 0, 0, 0, 0, 0, 0, 0];
        const u_counts = [0, 0, 0, 0];
        const h_counts = new Array(24).fill(0);
        const m_counts = {{}};
        const holiday_counts = {{}};
        const ems_counts = [0, 0, 0, 0, 0];
        const er_counts = [0, 0, 0, 0, 0, 0, 0, 0];
        const prov_map = {{}};

        const helmet_cross = {{
            'ไม่สวมหมวก': {{ hi: 0, non_hi: 0 }},
            'สวมหมวก': {{ hi: 0, non_hi: 0 }},
            'ไม่ทราบ': {{ hi: 0, non_hi: 0 }}
        }};

        const alc_by_age = {{
            '0-14 ปี (เด็ก)': {{ alcohol: 0, no_alcohol: 0 }},
            '15-24 ปี (เยาวชน)': {{ alcohol: 0, no_alcohol: 0 }},
            '25-59 ปี (วัยทำงาน)': {{ alcohol: 0, no_alcohol: 0 }},
            '60+ ปี (สูงอายุ)': {{ alcohol: 0, no_alcohol: 0 }}
        }};

        const len = currentRawRecords.length;
        for (let i = 0; i < len; i += 8) {{
            const pid = currentRawRecords[i];
            if (targetPid >= 0 && pid !== targetPid) continue;

            const sex = currentRawRecords[i + 1];
            if (f_sex > 0 && sex !== f_sex) continue;

            const ag = currentRawRecords[i + 2];
            if (f_ag > 0 && ag !== f_ag) continue;

            const vid = currentRawRecords[i + 3];
            if (f_vid >= 0 && vid !== f_vid) continue;

            const month_yr = currentRawRecords[i + 4];
            const month = month_yr & 15;
            const yid = (month_yr >> 4) & 15;
            const yrLabel = yearsList[yid] || '2569';

            if (f_yr !== '0' && yrLabel !== f_yr) continue;

            // Period filter
            if (f_period !== '0') {{
                if (f_period === 'Q1' && !(month >= 1 && month <= 3)) continue;
                else if (f_period === 'Q2' && !(month >= 4 && month <= 6)) continue;
                else if (f_period === 'Q3' && !(month >= 7 && month <= 9)) continue;
                else if (f_period === 'Q4' && !(month >= 10 && month <= 12)) continue;
                else if (f_period.length <= 2 && parseInt(f_period, 10) !== month) continue;
            }}

            const hld_hr = currentRawRecords[i + 5];
            const hld = (hld_hr >> 5) & 3;
            if (f_hld > 0 && hld !== f_hld) continue;

            const hr = hld_hr & 31;
            const flags1 = currentRawRecords[i + 6];
            const r1 = flags1 & 1;
            const r4 = (flags1 >> 1) & 3;
            const hi = (flags1 >> 3) & 1;
            const death = (flags1 >> 4) & 1;
            const admit = (flags1 >> 5) & 1;

            if (f_risk === 'alcohol' && !r1) continue;
            if (f_risk === 'no_helmet' && r4 !== 2) continue;
            if (f_risk === 'head_inj' && !hi) continue;
            if (f_risk === 'death' && !death) continue;
            if (f_risk === 'admit' && !admit) continue;

            const flags2 = currentRawRecords[i + 7];
            const ems = flags2 & 7;
            const er = (flags2 >> 3) & 7;
            const injp = (flags2 >> 6) & 3;

            total++;
            if (death) deaths++;
            if (admit) admits++;
            if (hi) head_inj++;
            if (r1) alc++;
            if (sex === 1) sex_m++; else if (sex === 2) sex_f++;

            if (vid === 1) {{
                motos++;
                if (r4 === 2) {{
                    no_helmet++;
                    if (hi) helmet_cross['ไม่สวมหมวก'].hi++; else helmet_cross['ไม่สวมหมวก'].non_hi++;
                }} else if (r4 === 1) {{
                    if (hi) helmet_cross['สวมหมวก'].hi++; else helmet_cross['สวมหมวก'].non_hi++;
                }} else {{
                    if (hi) helmet_cross['ไม่ทราบ'].hi++; else helmet_cross['ไม่ทราบ'].non_hi++;
                }}
            }}

            if (ag >= 0 && ag <= 4) age_counts[ag]++;
            if (vid >= 0 && vid <= 7) v_counts[vid]++;
            if (injp >= 0 && injp <= 3) u_counts[injp]++;
            if (hr >= 0 && hr < 24) h_counts[hr]++;

            const ageLabels = {{ 1: '0-14 ปี (เด็ก)', 2: '15-24 ปี (เยาวชน)', 3: '25-59 ปี (วัยทำงาน)', 4: '60+ ปี (สูงอายุ)' }};
            if (ageLabels[ag]) {{
                if (r1) alc_by_age[ageLabels[ag]].alcohol++;
                else alc_by_age[ageLabels[ag]].no_alcohol++;
            }}

            if (month >= 1 && month <= 12) {{
                const mKey = `${{MONTH_THAI[month]}} ${{yrLabel}}`;
                m_counts[mKey] = (m_counts[mKey] || 0) + 1;
            }}

            if (hld === 1) holiday_counts['ปีใหม่ (1-7 ม.ค.)'] = (holiday_counts['ปีใหม่ (1-7 ม.ค.)'] || 0) + 1;
            else if (hld === 2) holiday_counts['สงกรานต์ (11-17 เม.ย.)'] = (holiday_counts['สงกรานต์ (11-17 เม.ย.)'] || 0) + 1;

            if (ems >= 0 && ems <= 4) ems_counts[ems]++;
            if (er >= 1 && er <= 7) er_counts[er]++;

            const pName = provincesList[pid] || 'ไม่ระบุ';
            if (!prov_map[pName]) prov_map[pName] = {{ cases: 0, deaths: 0, admits: 0, head_inj: 0 }};
            prov_map[pName].cases++;
            if (death) prov_map[pName].deaths++;
            if (admit) prov_map[pName].admits++;
            if (hi) prov_map[pName].head_inj++;
        }}

        const filtered = {{
            total_cases: total,
            total_deaths: deaths,
            total_admits: admits,
            total_head_injury: head_inj,
            total_moto_cases: motos,
            total_no_helmet_moto: no_helmet,
            gender: {{ 'ชาย': sex_m, 'หญิง': sex_f }},
            age_groups: {{
                '0-14 ปี (เด็ก)': age_counts[1],
                '15-24 ปี (เยาวชน)': age_counts[2],
                '25-59 ปี (วัยทำงาน)': age_counts[3],
                '60+ ปี (สูงอายุ)': age_counts[4]
            }},
            vehicles: {{
                'รถจักรยานยนต์': v_counts[1],
                'รถปิคอัพ': v_counts[3],
                'รถเก๋ง / SUV': v_counts[2],
                'รถจักรยาน': v_counts[4],
                'รถบรรทุก / พ่วง': v_counts[5],
                'รถโดยสาร / รถตู้': v_counts[6],
                'แท็กซี่ / สามล้อ': v_counts[7],
                'อื่นๆ / ไม่ระบุ': v_counts[0]
            }},
            user_types: {{
                'ผู้ขับขี่': u_counts[2],
                'ผู้โดยสาร': u_counts[3],
                'คนเดินเท้า': u_counts[1],
                'อื่นๆ/ไม่ระบุ': u_counts[0]
            }},
            cross_helmet_head_injury: helmet_cross,
            alcohol_by_age: alc_by_age,
            monthly: m_counts,
            daily_peaks: holiday_counts,
            hourly: h_counts,
            provinces: prov_map,
            ems: {{
                'FR (เบื้องต้น)': ems_counts[3],
                'BLS (พื้นฐาน)': ems_counts[2],
                'ALS (ขั้นสูง)': ems_counts[1],
                'ILS (ระดับกลาง)': ems_counts[4],
                'ไม่ใช้/มาเอง': ems_counts[0]
            }},
            er_status: {{
                'จำหน่ายกลับบ้าน': er_counts[2],
                'รับไว้รักษา (Admit)': er_counts[7],
                'ส่งต่อไป รพ. อื่น': er_counts[3],
                'ปฏิเสธการรักษา': er_counts[4],
                'หนีกลับ': er_counts[5],
                'เสียชีวิตใน ER': er_counts[6],
                'เสียชีวิตก่อนถึง ER': er_counts[1]
            }}
        }};

        currentFilteredStats = filtered;
        renderAllData(filtered);
    }}

    // Render Data into UI
    function renderAllData(data) {{
        document.getElementById('kpiCases').textContent = fnum(data.total_cases);
        document.getElementById('kpiDeaths').textContent = fnum(data.total_deaths);
        document.getElementById('kpiAdmits').textContent = fnum(data.total_admits);
        document.getElementById('kpiHeadInj').textContent = fnum(data.total_head_injury);
        document.getElementById('kpiMotos').textContent = fnum(data.total_moto_cases);
        document.getElementById('kpiNoHelmet').textContent = fnum(data.total_no_helmet_moto);

        const cfr = data.total_cases > 0 ? ((data.total_deaths / data.total_cases) * 100).toFixed(2) : '0.00';
        document.getElementById('kpiCFR').textContent = `CFR ${{cfr}}%`;

        const admitRate = data.total_cases > 0 ? ((data.total_admits / data.total_cases) * 100).toFixed(1) : '0.0';
        document.getElementById('kpiAdmitRate').textContent = `${{admitRate}}%`;

        const hiRate = data.total_cases > 0 ? ((data.total_head_injury / data.total_cases) * 100).toFixed(1) : '0.0';
        document.getElementById('kpiHIRate').textContent = `${{hiRate}}%`;

        const motoRate = data.total_cases > 0 ? ((data.total_moto_cases / data.total_cases) * 100).toFixed(1) : '0.0';
        document.getElementById('kpiMotoRate').textContent = `${{motoRate}}%`;

        const noHelRate = data.total_moto_cases > 0 ? ((data.total_no_helmet_moto / data.total_moto_cases) * 100).toFixed(1) : '0.0';
        document.getElementById('kpiNoHelmetRate').textContent = `${{noHelRate}}%`;

        const male = data.gender['ชาย'] || 0;
        const female = data.gender['หญิง'] || 0;
        const totalGender = male + female;
        const mPct = totalGender > 0 ? ((male / totalGender) * 100).toFixed(1) : '0.0';
        const fPct = totalGender > 0 ? ((female / totalGender) * 100).toFixed(1) : '0.0';
        document.getElementById('kpiCasesSub').textContent = `ชาย ${{mPct}}% | หญิง ${{fPct}}%`;

        // Relative risk text
        const hel = data.cross_helmet_head_injury || {{}};
        const noHelHI = hel['ไม่สวมหมวก'] ? hel['ไม่สวมหมวก'].hi : 0;
        const noHelTotal = hel['ไม่สวมหมวก'] ? (hel['ไม่สวมหมวก'].hi + hel['ไม่สวมหมวก'].non_hi) : 0;
        const helHI = hel['สวมหมวก'] ? hel['สวมหมวก'].hi : 0;
        const helTotal = hel['สวมหมวก'] ? (hel['สวมหมวก'].hi + hel['สวมหมวก'].non_hi) : 0;
        
        if (noHelTotal > 0 && helTotal > 0 && helHI > 0) {{
            const rr = ((noHelHI / noHelTotal) / (helHI / helTotal)).toFixed(1);
            document.getElementById('relativeRiskContent').innerHTML = 
                `ผู้ขับขี่และโดยสารรถจักรยานยนต์ที่ <strong>ไม่สวมหมวกนิรภัย มีโอกาสเกิดการบาดเจ็บที่ศีรษะ (Head Injury) สูงกว่ากลุ่มที่สวมหมวกถึง ${{rr}} เท่า</strong> (พบ Head Injury ในกลุ่มไม่สวมหมวก ${{fnum(noHelHI)}} ราย เทียบกับกลุ่มสวมหมวก ${{fnum(helHI)}} ราย)`;
        }} else {{
            document.getElementById('relativeRiskContent').textContent = 'ไม่มีข้อมูลเพียงพอสำหรับการคำนวณ Relative Risk';
        }}

        // Render Map, Regional Breakdown & Table
        renderThailandSvgMap(data.provinces);
        renderRegionalBreakdown(data.provinces);
        renderProvinceTable(data.provinces);
        updateCharts(data);
    }}

    function renderProvinceTable(provs) {{
        const tbody = document.getElementById('provTableBody');
        tbody.innerHTML = '';
        const sorted = Object.entries(provs || {{}}).sort((a,b) => b[1].cases - a[1].cases);

        if (sorted.length === 0) {{
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; padding:30px; color:var(--text-muted);"><i class="fa-solid fa-folder-open"></i> ไม่มีข้อมูลในระบบ (กรุณานำเข้าไฟล์ CSV หรือโหลดข้อมูลตัวอย่าง)</td></tr>';
            return;
        }}

        sorted.forEach(([name, d], idx) => {{
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td style="font-weight:600; color:var(--text-muted);">${{idx + 1}}</td>
                <td style="font-weight:600;">${{name}}</td>
                <td style="text-align:right;">${{fnum(d.cases)}}</td>
                <td style="text-align:right; color:var(--danger); font-weight:600;">${{fnum(d.deaths)}}</td>
                <td style="text-align:right;">${{fnum(d.admits)}}</td>
                <td style="text-align:right;">${{fnum(d.head_inj)}}</td>
            `;
            tbody.appendChild(tr);
        }});
    }}

    function filterProvinceTable() {{
        const q = document.getElementById('provTableSearch').value.toLowerCase().trim();
        const rows = document.querySelectorAll('#provTableBody tr');
        rows.forEach(r => {{
            if (r.children.length > 1) {{
                const name = r.children[1].textContent.toLowerCase();
                r.style.display = name.includes(q) ? '' : 'none';
            }}
        }});
    }}

    function destroyChart(id) {{
        if (charts[id]) charts[id].destroy();
    }}

    function updateCharts(data) {{
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        const textColor = isDark ? '#f8fafc' : '#0f172a';
        const mutedColor = isDark ? '#94a3b8' : '#64748b';
        const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';

        Chart.defaults.color = mutedColor;
        Chart.defaults.font.family = "'Anuphan', sans-serif";

        // 1. Age Group
        destroyChart('chartAge');
        const ageCtx = document.getElementById('chartAge').getContext('2d');
        charts['chartAge'] = new Chart(ageCtx, {{
            type: 'doughnut',
            data: {{
                labels: Object.keys(data.age_groups || {{}}),
                datasets: [{{
                    data: Object.values(data.age_groups || {{}}),
                    backgroundColor: ['#38bdf8', '#0284c7', '#0369a1', '#f59e0b', '#94a3b8'],
                    borderWidth: 2,
                    borderColor: isDark ? '#131d33' : '#ffffff'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ position: 'bottom', labels: {{ color: textColor, padding: 10 }} }} }}
            }}
        }});

        // 2. Gender & Disposition
        destroyChart('chartGender');
        const gCtx = document.getElementById('chartGender').getContext('2d');
        charts['chartGender'] = new Chart(gCtx, {{
            type: 'bar',
            data: {{
                labels: ['เพศชาย', 'เพศหญิง', 'รับรักษา Admit', 'เสียชีวิต'],
                datasets: [{{
                    data: [(data.gender ? data.gender['ชาย'] : 0), (data.gender ? data.gender['หญิง'] : 0), data.total_admits, data.total_deaths],
                    backgroundColor: ['#0284c7', '#ec4899', '#f59e0b', '#ef4444'],
                    borderRadius: 4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ grid: {{ display: false }} }},
                    y: {{ grid: {{ color: gridColor }} }}
                }}
            }}
        }});

        // 3. Vehicles
        destroyChart('chartVehicles');
        const vCtx = document.getElementById('chartVehicles').getContext('2d');
        const vEntries = Object.entries(data.vehicles || {{}}).sort((a,b) => b[1] - a[1]);
        charts['chartVehicles'] = new Chart(vCtx, {{
            type: 'bar',
            data: {{
                labels: vEntries.map(e => e[0]),
                datasets: [{{
                    data: vEntries.map(e => e[1]),
                    backgroundColor: vEntries.map((e, idx) => idx === 0 ? '#ef4444' : '#0284c7'),
                    borderRadius: 4
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ grid: {{ color: gridColor }} }},
                    y: {{ grid: {{ display: false }} }}
                }}
            }}
        }});

        // 4. Helmet vs Head Injury (DYNAMIC FROM DATA)
        destroyChart('chartHelmet');
        const hCtx = document.getElementById('chartHelmet').getContext('2d');
        const helData = data.cross_helmet_head_injury || {{
            'ไม่สวมหมวก': {{ hi: 0, non_hi: 0 }}, 'สวมหมวก': {{ hi: 0, non_hi: 0 }}, 'ไม่ทราบ': {{ hi: 0, non_hi: 0 }}
        }};
        charts['chartHelmet'] = new Chart(hCtx, {{
            type: 'bar',
            data: {{
                labels: ['ไม่สวมหมวกนิรภัย', 'สวมหมวกนิรภัย', 'ไม่ทราบ'],
                datasets: [
                    {{
                        label: 'บาดเจ็บศีรษะ (Head Injury)',
                        data: [
                            helData['ไม่สวมหมวก'] ? helData['ไม่สวมหมวก'].hi : 0,
                            helData['สวมหมวก'] ? helData['สวมหมวก'].hi : 0,
                            helData['ไม่ทราบ'] ? helData['ไม่ทราบ'].hi : 0
                        ],
                        backgroundColor: '#ef4444',
                        borderRadius: 4
                    }},
                    {{
                        label: 'ไม่บาดเจ็บศีรษะ (Non HI)',
                        data: [
                            helData['ไม่สวมหมวก'] ? helData['ไม่สวมหมวก'].non_hi : 0,
                            helData['สวมหมวก'] ? helData['สวมหมวก'].non_hi : 0,
                            helData['ไม่ทราบ'] ? helData['ไม่ทราบ'].non_hi : 0
                        ],
                        backgroundColor: '#10b981',
                        borderRadius: 4
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ position: 'bottom', labels: {{ color: textColor }} }} }},
                scales: {{
                    x: {{ stacked: true, grid: {{ display: false }} }},
                    y: {{ stacked: true, grid: {{ color: gridColor }} }}
                }}
            }}
        }});

        // 5. Alcohol by Age (DYNAMIC FROM DATA)
        destroyChart('chartAlcohol');
        const alcCtx = document.getElementById('chartAlcohol').getContext('2d');
        const alcData = data.alcohol_by_age || {{}};
        const alcLabels = ['15-24 ปี (เยาวชน)', '25-59 ปี (วัยทำงาน)', '60+ ปี (สูงอายุ)', '0-14 ปี (เด็ก)'];
        charts['chartAlcohol'] = new Chart(alcCtx, {{
            type: 'bar',
            data: {{
                labels: alcLabels,
                datasets: [
                    {{
                        label: 'ดื่มแอลกอฮอล์',
                        data: alcLabels.map(k => (alcData[k] ? alcData[k].alcohol : 0)),
                        backgroundColor: '#f59e0b',
                        borderRadius: 4
                    }},
                    {{
                        label: 'ไม่ดื่มแอลกอฮอล์',
                        data: alcLabels.map(k => (alcData[k] ? alcData[k].no_alcohol : 0)),
                        backgroundColor: '#64748b',
                        borderRadius: 4
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ position: 'bottom', labels: {{ color: textColor }} }} }},
                scales: {{
                    x: {{ grid: {{ display: false }} }},
                    y: {{ grid: {{ color: gridColor }} }}
                }}
            }}
        }});

        // 6. User Types (DYNAMIC FROM DATA)
        destroyChart('chartUserTypes');
        const utCtx = document.getElementById('chartUserTypes').getContext('2d');
        const uTypes = data.user_types || {{}};
        charts['chartUserTypes'] = new Chart(utCtx, {{
            type: 'pie',
            data: {{
                labels: Object.keys(uTypes),
                datasets: [{{
                    data: Object.values(uTypes),
                    backgroundColor: ['#0284c7', '#38bdf8', '#f97316', '#94a3b8']
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ position: 'bottom', labels: {{ color: textColor }} }} }}
            }}
        }});

        // 7. Monthly (DYNAMIC FROM DATA)
        destroyChart('chartMonthly');
        const mCtx = document.getElementById('chartMonthly').getContext('2d');
        const mData = data.monthly || {{}};
        charts['chartMonthly'] = new Chart(mCtx, {{
            type: 'line',
            data: {{
                labels: Object.keys(mData),
                datasets: [{{
                    label: 'จำนวนผู้บาดเจ็บ',
                    data: Object.values(mData),
                    borderColor: '#0284c7',
                    backgroundColor: 'rgba(2, 132, 199, 0.15)',
                    fill: true,
                    tension: 0.35,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ grid: {{ display: false }} }},
                    y: {{ grid: {{ color: gridColor }} }}
                }}
            }}
        }});

        // 8. Holidays (DYNAMIC FROM DATA)
        destroyChart('chartHolidays');
        const hldCtx = document.getElementById('chartHolidays').getContext('2d');
        const hldData = data.daily_peaks || {{}};
        charts['chartHolidays'] = new Chart(hldCtx, {{
            type: 'bar',
            data: {{
                labels: Object.keys(hldData),
                datasets: [{{
                    label: 'ผู้บาดเจ็บ',
                    data: Object.values(hldData),
                    backgroundColor: Object.keys(hldData).map(k => k.includes('สงกรานต์') ? '#ef4444' : '#0284c7'),
                    borderRadius: 4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ grid: {{ display: false }}, ticks: {{ maxRotation: 45, minRotation: 45 }} }},
                    y: {{ grid: {{ color: gridColor }} }}
                }}
            }}
        }});

        // 9. Hourly
        destroyChart('chartHourly');
        const hrCtx = document.getElementById('chartHourly').getContext('2d');
        charts['chartHourly'] = new Chart(hrCtx, {{
            type: 'line',
            data: {{
                labels: Array.from({{ length: 24 }}, (_, i) => `${{i}}:00 น.`),
                datasets: [{{
                    label: 'ผู้บาดเจ็บตามช่วงเวลา',
                    data: data.hourly || new Array(24).fill(0),
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.15)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ grid: {{ display: false }} }},
                    y: {{ grid: {{ color: gridColor }} }}
                }}
            }}
        }});

        // 10. Top 15 Provinces
        destroyChart('chartTopProv');
        const pCtx = document.getElementById('chartTopProv').getContext('2d');
        const top15 = Object.entries(data.provinces || {{}}).sort((a,b) => b[1].cases - a[1].cases).slice(0, 15);
        charts['chartTopProv'] = new Chart(pCtx, {{
            type: 'bar',
            data: {{
                labels: top15.map(p => p[0]),
                datasets: [{{
                    label: 'ผู้บาดเจ็บ',
                    data: top15.map(p => p[1].cases),
                    backgroundColor: '#0284c7',
                    borderRadius: 4
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ grid: {{ color: gridColor }} }},
                    y: {{ grid: {{ display: false }} }}
                }}
            }}
        }});

        // 11. EMS
        destroyChart('chartEMS');
        const emsCtx = document.getElementById('chartEMS').getContext('2d');
        const emsEntries = Object.entries(data.ems || {{}}).sort((a,b) => b[1] - a[1]);
        charts['chartEMS'] = new Chart(emsCtx, {{
            type: 'doughnut',
            data: {{
                labels: emsEntries.map(e => e[0]),
                datasets: [{{
                    data: emsEntries.map(e => e[1]),
                    backgroundColor: ['#64748b', '#f59e0b', '#0284c7', '#ef4444', '#10b981']
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ position: 'bottom', labels: {{ color: textColor }} }} }}
            }}
        }});

        // 12. ER Disposition
        destroyChart('chartER');
        const erCtx = document.getElementById('chartER').getContext('2d');
        const erEntries = Object.entries(data.er_status || {{}}).sort((a,b) => b[1] - a[1]);
        charts['chartER'] = new Chart(erCtx, {{
            type: 'bar',
            data: {{
                labels: erEntries.map(e => e[0]),
                datasets: [{{
                    label: 'จำนวนผู้ป่วย',
                    data: erEntries.map(e => e[1]),
                    backgroundColor: ['#10b981', '#f59e0b', '#3b82f6', '#64748b', '#ef4444', '#dc2626', '#94a3b8'],
                    borderRadius: 4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ grid: {{ display: false }}, ticks: {{ maxRotation: 25, minRotation: 25 }} }},
                    y: {{ grid: {{ color: gridColor }} }}
                }}
            }}
        }});
    }}

    function refreshChartsWithCurrentData() {{
        if (currentFilteredStats) updateCharts(currentFilteredStats);
        else if (currentRawRecords && currentRawRecords.length === 0) updateCharts(getEmptyZeroStats());
        else updateCharts(masterData);
    }}

    // ADVANCED MULTI-FILE / MULTI-YEAR CSV IMPORT WITH DEDUPLICATION
    function handleMultipleFileSelect(evt) {{
        const files = Array.from(evt.target.files);
        if (!files.length) return;
        processMultipleCSVFiles(files);
    }}

    const dropzone = document.getElementById('dropzone');
    dropzone.addEventListener('dragover', (e) => {{
        e.preventDefault();
        dropzone.style.background = 'var(--primary-light)';
    }});
    dropzone.addEventListener('dragleave', () => {{
        dropzone.style.background = 'var(--bg-card-subtle)';
    }});
    dropzone.addEventListener('drop', (e) => {{
        e.preventDefault();
        dropzone.style.background = 'var(--bg-card-subtle)';
        if (e.dataTransfer.files.length) {{
            processMultipleCSVFiles(Array.from(e.dataTransfer.files));
        }}
    }});

    function processMultipleCSVFiles(files) {{
        const csvFiles = files.filter(f => f.name.toLowerCase().endsWith('.csv'));
        if (!csvFiles.length) {{
            alert('กรุณาเลือกไฟล์ที่มีนามสกุล .csv เท่านั้น');
            return;
        }}

        const mode = document.querySelector('input[name="importMode"]:checked').value;
        const pBar = document.getElementById('importProgressBar');
        const pText = document.getElementById('importStatusText');
        const pFill = document.getElementById('importFill');
        const pPct = document.getElementById('importPct');
        const logBox = document.getElementById('importStatsLog');

        pBar.style.display = 'block';
        logBox.style.display = 'none';

        if (mode === 'replace') {{
            currentRawRecords = new Uint8Array(0);
            deduplicationSet.clear();
            importedFileNames = [];
            yearsList = [];
        }}

        let fileIndex = 0;
        let totalNewRows = 0;
        let totalDuplicatesSkipped = 0;
        let newRecordsBuffer = [];

        function parseNextFile() {{
            if (fileIndex >= csvFiles.length) {{
                pFill.style.width = '100%';
                pPct.textContent = '100%';
                pText.textContent = 'กำลังผสานและอัปเดตฐานข้อมูล...';

                const additionalBytes = new Uint8Array(newRecordsBuffer);
                const existingLength = (currentRawRecords ? currentRawRecords.length : 0);
                const combined = new Uint8Array(existingLength + additionalBytes.length);
                if (existingLength > 0) combined.set(currentRawRecords, 0);
                combined.set(additionalBytes, existingLength);
                currentRawRecords = combined;

                const totalCasesNow = currentRawRecords.length / 8;
                document.getElementById('filterStatusBadge').innerHTML = 
                    `<i class="fa-solid fa-circle-check" style="color:var(--success);"></i> นำเข้าข้อมูลสำเร็จ (${{fnum(totalCasesNow)}} เคส จาก ${{importedFileNames.length}} ไฟล์)`;

                logBox.style.display = 'block';
                logBox.innerHTML = `
                    <div style="font-weight:700; color:var(--success); margin-bottom:4px;">
                        <i class="fa-solid fa-circle-check"></i> ประมวลผลสำเร็จรวม ${{csvFiles.length}} ไฟล์!
                    </div>
                    <div>• รายการที่นำเข้าใหม่: <strong>${{fnum(totalNewRows)}}</strong> รายการ</div>
                    <div>• รายการซ้ำที่คัดกรองออก (Deduplicated): <strong style="color:var(--warning);">${{fnum(totalDuplicatesSkipped)}}</strong> รายการ</div>
                    <div>• ฐานข้อมูลรวมปัจจุบัน: <strong>${{fnum(totalCasesNow)}}</strong> รายการ</div>
                    <div style="margin-top:6px; color:var(--text-muted); font-size:0.75rem;">
                        ไฟล์ที่นำเข้า: ${{importedFileNames.join(', ')}}
                    </div>
                `;

                setupProvinceDatalist();
                setupYearSelector();
                updateDynamicAcademicTitle();

                resetAllFilters();
                executeFastFilter();
                return;
            }}

            const file = csvFiles[fileIndex];
            importedFileNames.push(file.name);
            pText.textContent = `กำลังอ่านไฟล์ที่ ${{fileIndex + 1}}/${{csvFiles.length}}: ${{file.name}}...`;

            Papa.parse(file, {{
                header: true,
                skipEmptyLines: true,
                transformHeader: function(h) {{ return h.trim().toLowerCase(); }},
                chunkSize: 1024 * 1024 * 4,
                chunk: function(results) {{
                    results.data.forEach(r => {{
                        const rawDate = (r.adate || r.hdate || '').trim();
                        const rawTime = (r.atime || r.htime || '').trim();
                        const prov = (r.prov || '').trim();
                        const age = (r.age || '').trim();
                        const sex = (r.sex || '').trim();
                        const injt = (r.injt || '').trim();
                        const injp = (r.injp || '').trim();
                        const staer = (r.staer || '').trim();
                        const staward = (r.staward || '').trim();

                        // Unique Case Fingerprint for Deduplication
                        const fingerprint = `${{prov}}|${{rawDate}}|${{rawTime}}|${{age}}|${{sex}}|${{injt}}|${{injp}}|${{staer}}`;
                        if (deduplicationSet.has(fingerprint)) {{
                            totalDuplicatesSkipped++;
                            return;
                        }}
                        deduplicationSet.add(fingerprint);
                        totalNewRows++;

                        // Register province dynamically
                        let pid = provincesList.indexOf(prov);
                        if (pid < 0 && prov) {{
                            pid = provincesList.length;
                            provincesList.push(prov);
                        }}
                        if (pid < 0) pid = 0;

                        const sexVal = sex === '1' ? 1 : (sex === '2' ? 2 : 0);
                        const ageNum = parseInt(age, 10);
                        let agVal = 0;
                        if (!isNaN(ageNum) && ageNum >= 0) {{
                            if (ageNum <= 14) agVal = 1;
                            else if (ageNum <= 24) agVal = 2;
                            else if (ageNum <= 59) agVal = 3;
                            else agVal = 4;
                        }}

                        let vidVal = 0;
                        if (['2', '02', '21', '021', '22', '022', '23', '023'].includes(injt)) vidVal = 1;
                        else if (['4', '04', '41', '041'].includes(injt)) vidVal = 2;
                        else if (['5', '05'].includes(injt)) vidVal = 3;
                        else if (['1', '01', '11', '011'].includes(injt)) vidVal = 4;
                        else if (['6', '06', '7', '07'].includes(injt)) vidVal = 5;
                        else if (['8', '08', '9', '09', '18'].includes(injt)) vidVal = 6;
                        else if (['3', '03', '10'].includes(injt)) vidVal = 7;

                        // Robust Date & Year extraction
                        let month = 0, yid = 0, hld = 0, hr = 0;
                        const dateInfo = parseISDate(rawDate);
                        if (dateInfo) {{
                            month = dateInfo.month;
                            hr = dateInfo.hour;
                            const yrBE = dateInfo.yearStr;
                            
                            let yrIndex = yearsList.indexOf(yrBE);
                            if (yrIndex < 0 && yrBE) {{
                                yrIndex = yearsList.length;
                                yearsList.push(yrBE);
                            }}
                            yid = Math.max(0, yrIndex);

                            if (month === 1 && dateInfo.day <= 7) hld = 1;
                            else if (month === 4 && dateInfo.day >= 11 && dateInfo.day <= 17) hld = 2;
                        }}

                        if (!hr && rawTime && rawTime.includes(':')) {{
                            const ph = parseInt(rawTime.split(':')[0], 10);
                            if (!isNaN(ph) && ph >= 0 && ph < 24) hr = ph;
                        }}

                        const r1 = (r.risk1 || '').trim() === '1' ? 1 : 0;
                        const r4Raw = (r.risk4 || '').trim();
                        const r4 = r4Raw === '1' ? 1 : (r4Raw === '0' ? 2 : 0);
                        
                        const hiRaw = (r.head_injury || '').trim().toUpperCase();
                        const hi = (hiRaw === '1' || hiRaw === 'HI') ? 1 : 0;
                        
                        const death = (['1', '6'].includes(staer) || staward === '5') ? 1 : 0;
                        const admit = staer === '7' ? 1 : 0;

                        const emsRaw = (r.ems || '').trim();
                        const emsVal = ['1','2','3','4'].includes(emsRaw) ? parseInt(emsRaw, 10) : 0;
                        const erVal = (staer.length === 1 && parseInt(staer, 10) >= 1 && parseInt(staer, 10) <= 7) ? parseInt(staer, 10) : 0;
                        
                        let injpVal = 0;
                        if (injp === '1') injpVal = 1;
                        else if (injp === '2') injpVal = 2;
                        else if (injp === '3') injpVal = 3;

                        const month_yr = ((yid & 15) << 4) | (month & 15);
                        const hld_hr = ((hld & 3) << 5) | (hr & 31);
                        const flags1 = (r1 & 1) | ((r4 & 3) << 1) | ((hi & 1) << 3) | ((death & 1) << 4) | ((admit & 1) << 5);
                        const flags2 = (emsVal & 7) | ((erVal & 7) << 3) | ((injpVal & 3) << 6);

                        newRecordsBuffer.push(pid, sexVal, agVal, vidVal, month_yr, hld_hr, flags1, flags2);
                    }});

                    const progressPct = Math.round(((fileIndex + 0.5) / csvFiles.length) * 100);
                    pFill.style.width = progressPct + '%';
                    pPct.textContent = progressPct + '%';
                }},
                complete: function() {{
                    fileIndex++;
                    parseNextFile();
                }},
                error: function(err) {{
                    alert('เกิดข้อผิดพลาดในการอ่านไฟล์ ' + file.name + ': ' + err.message);
                    fileIndex++;
                    parseNextFile();
                }}
            }});
        }}

        parseNextFile();
    }}

    // Startup
    window.addEventListener('DOMContentLoaded', () => {{
        if (localStorage.getItem('is_theme') === 'dark') {{
            document.documentElement.setAttribute('data-theme', 'dark');
            document.getElementById('themeToggle').innerHTML = '<i class="fa-solid fa-sun"></i>';
        }}
        setupProvinceDatalist();
        setupYearSelector();
        updateDynamicAcademicTitle();
        
        // Start by rendering default 2026 data
        renderAllData(masterData);
        setTimeout(initBinaryDataset, 120);
    }});
</script>
</body>
</html>
'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html_code)

print("SUCCESS: index.html fully built and ready!")
print(f"File size: {len(html_code)/1024:.2f} KB")
