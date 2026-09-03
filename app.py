<!DOCTYPE html>
<html lang="vi" class="dark scroll-smooth">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>AIC 2026 - AI Retrieval Operations Center</title>
  
  <!-- Fonts: Inter & JetBrains Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
  
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['Inter', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace'],
          },
          colors: {
            brand: {
              primary: '#6366F1',
              secondary: '#0EA5E9',
              accent: '#10B981',
              darkBg: '#0F172A',
              cardBg: '#1E293B',
            }
          }
        }
      }
    }
  </script>
</head>
<body class="bg-[#0F172A] text-slate-100 font-sans antialiased min-h-screen flex flex-col selection:bg-indigo-500 selection:text-white">

  <!-- TOP NAVIGATION HEADER -->
  <header class="sticky top-0 z-50 bg-[#0F172A]/90 backdrop-blur-md border-b border-slate-800 px-4 lg:px-6 py-3 transition-all">
    <div class="max-w-[1760px] mx-auto flex items-center justify-between gap-4">
      
      <!-- Logo & System Status -->
      <div class="flex items-center gap-4 shrink-0">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 via-sky-500 to-emerald-500 p-[2px] cursor-pointer hover:shadow-lg hover:shadow-indigo-500/20 transition-all">
            <div class="w-full h-full bg-slate-900 rounded-[10px] flex items-center justify-center">
              <svg class="w-5 h-5 text-indigo-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 2a10 10 0 1 0 10 10H12V2z"></path>
                <path d="M12 12L2.5 7.5"></path>
                <path d="m12 12 8.5 4.5"></path>
              </svg>
            </div>
          </div>
          <div>
            <div class="flex items-center gap-2">
              <span class="font-bold text-lg tracking-wider text-white font-mono">AIC<span class="text-indigo-400">.ENGINE</span></span>
              <span class="text-[10px] font-mono font-semibold uppercase px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">v2.4 PRO</span>
            </div>
            <p class="text-xs text-slate-400 font-mono hidden sm:block">AI Challenge Video Retrieval Hub</p>
          </div>
        </div>

        <div class="h-6 w-[1px] bg-slate-800 hidden md:block"></div>

        <!-- Live Server Status Indicator -->
        <div class="hidden md:flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/60 text-xs text-slate-300 font-mono">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span>API: Connected (18ms)</span>
        </div>
      </div>

      <!-- Dataset Selector & Submission Quota -->
      <div class="flex items-center gap-3">
        <!-- Dataset Dropdown -->
        <div class="relative">
          <label for="dataset-select" class="sr-only">Select Dataset</label>
          <select id="dataset-select" class="cursor-pointer appearance-none bg-slate-800 hover:bg-slate-700/80 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-2 pr-8 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono transition-all">
            <option value="lse_2026">Dataset: LSE_2026_Batch_01 (120k Frames)</option>
            <option value="ktsc_v2">Dataset: KTSC_Video_V2 (85k Frames)</option>
            <option value="kis_2025">Dataset: KIS_Challenge_2025 (200k Frames)</option>
          </select>
          <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
          </div>
        </div>

        <!-- Submissions Counter -->
        <div class="hidden sm:flex items-center gap-2 px-3 py-2 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22 4 12 14.01 9 11.01"></polyline>
          </svg>
          <span>Submit Limit: <strong>18/200</strong></span>
        </div>

        <!-- Quick Help Button -->
        <button class="cursor-pointer p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500" title="Shortcuts & Documentation">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
        </button>
      </div>

    </div>
  </header>

  <!-- MAIN WORKSPACE LAYOUT -->
  <main class="flex-1 max-w-[1760px] w-full mx-auto p-4 lg:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">

    <!-- LEFT & CENTER COLUMN: SEARCH ENGINE & RESULTS (9 COLUMNS) -->
    <div class="lg:col-span-8 xl:col-span-9 flex flex-col gap-6">
      
      <!-- AI MULTI-MODAL QUERY CENTER CARD -->
      <section class="bg-slate-800/60 backdrop-blur-md rounded-2xl border border-slate-700/60 p-5 shadow-xl transition-all">
        
        <!-- Search Mode Switcher Tabs -->
        <div class="flex items-center gap-2 mb-4 overflow-x-auto pb-1 border-b border-slate-700/50">
          <button class="cursor-pointer flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 text-white text-xs font-medium shadow-md shadow-indigo-600/30 transition-all">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
            <span>Text Prompt Search</span>
          </button>
          
          <button class="cursor-pointer flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition-all">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
            <span>Image-to-Image (CLIP)</span>
          </button>

          <button class="cursor-pointer flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition-all">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line></svg>
            <span>ASR / Audio Transcript</span>
          </button>

          <button class="cursor-pointer flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition-all">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7V4h3"></path><path d="M20 7V4h-3"></path><path d="M4 17v3h3"></path><path d="M20 17v3h-3"></path><rect x="9" y="9" width="6" height="6"></rect></svg>
            <span>OCR / Text in Video</span>
          </button>
        </div>

        <!-- Main Query Input Field -->
        <div class="relative mb-4">
          <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
            <svg class="w-5 h-5 text-indigo-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          </div>
          <input 
            type="text" 
            placeholder="Mô tả chi tiết bằng tiếng Việt hoặc tiếng Anh... (VD: Người mặc áo phao màu xanh lá đi xe đạp qua ngã tư lúc trời mưa)" 
            class="w-full bg-slate-900/90 border border-slate-700 focus:border-indigo-500 rounded-xl pl-12 pr-32 py-3.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/40 font-sans transition-all shadow-inner"
            value="Người phụ nữ áo dài đỏ đi bộ ngang qua cửa hàng bánh mì Saigon"
          />
          <div class="absolute inset-y-1.5 right-1.5 flex items-center gap-2">
            <button class="cursor-pointer px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-lg shadow-indigo-600/30 transition-all active:scale-95">
              <span>Execute Search</span>
              <span class="bg-indigo-700 text-[10px] px-1.5 py-0.5 rounded font-mono">↵ Enter</span>
            </button>
          </div>
        </div>

        <!-- Tag Quick Injectors & Active Filters -->
        <div class="flex flex-wrap items-center justify-between gap-3 text-xs">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="text-slate-400 font-mono text-[11px]">Quick Tags:</span>
            <button class="cursor-pointer px-2.5 py-1 rounded-md bg-slate-700/50 hover:bg-slate-700 text-indigo-300 border border-slate-600/50 font-mono text-[11px] transition-all">#ao_dai_do</button>
            <button class="cursor-pointer px-2.5 py-1 rounded-md bg-slate-700/50 hover:bg-slate-700 text-indigo-300 border border-slate-600/50 font-mono text-[11px] transition-all">#banh_mi</button>
            <button class="cursor-pointer px-2.5 py-1 rounded-md bg-slate-700/50 hover:bg-slate-700 text-indigo-300 border border-slate-600/50 font-mono text-[11px] transition-all">#pedestrian</button>
            <button class="cursor-pointer px-2.5 py-1 rounded-md bg-slate-700/50 hover:bg-slate-700 text-indigo-300 border border-slate-600/50 font-mono text-[11px] transition-all">#street_cam</button>
          </div>

          <!-- Advanced Filters Toggle -->
          <button class="cursor-pointer flex items-center gap-1.5 text-sky-400 hover:text-sky-300 font-medium transition-all">
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon></svg>
            <span>Advanced Filters (FPS, Confidence)</span>
          </button>
        </div>

      </section>

      <!-- RESULTS HEADER BAR -->
      <div class="flex items-center justify-between gap-4 flex-wrap px-1">
        <div class="flex items-center gap-3">
          <h2 class="text-base font-bold tracking-tight text-white flex items-center gap-2">
            <span>Query Results</span>
            <span class="px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300 text-xs font-mono font-normal">Found: 1,420 keyframes</span>
          </h2>
        </div>

        <div class="flex items-center gap-3">
          <label for="grid-sort" class="sr-only">Sort Results</label>
          <span class="text-xs text-slate-400 font-mono hidden sm:inline">Sort by:</span>
          <select id="grid-sort" class="cursor-pointer bg-slate-800 border border-slate-700 text-slate-300 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-indigo-500 font-mono">
            <option value="relevance">Similarity Score (High → Low)</option>
            <option value="time_asc">Chronological (Ascending)</option>
            <option value="time_desc">Chronological (Descending)</option>
          </select>

          <div class="h-4 w-[1px] bg-slate-800"></div>

          <!-- Display Layout Grid Switcher -->
          <div class="flex items-center bg-slate-800 p-1 rounded-lg border border-slate-700">
            <button class="cursor-pointer p-1.5 rounded bg-indigo-600 text-white transition-all" title="Dense Grid">
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
            </button>
            <button class="cursor-pointer p-1.5 rounded text-slate-400 hover:text-white transition-all" title="List View">
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"></line><line x1="8" y1="12" x2="21" y2="12"></line><line x1="8" y1="18" x2="21" y2="18"></line><line x1="3" y1="6" x2="3.01" y2="6"></line><line x1="3" y1="12" x2="3.01" y2="12"></line><line x1="3" y1="18" x2="3.01" y2="18"></line></svg>
            </button>
          </div>
        </div>
      </div>

      <!-- KEYFRAME RESULTS GRID -->
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        
        <!-- CARD 1 -->
        <div class="group relative bg-slate-800/80 hover:bg-slate-800 rounded-xl border border-slate-700/80 hover:border-indigo-500/80 overflow-hidden shadow-lg transition-all duration-200 hover:-translate-y-1">
          <!-- Thumbnail Container -->
          <div class="relative aspect-video bg-slate-950 overflow-hidden cursor-pointer">
            <!-- Frame Placeholder Image simulation -->
            <div class="w-full h-full bg-gradient-to-br from-slate-900 via-indigo-950/40 to-slate-900 flex items-center justify-center relative">
              <svg class="w-12 h-12 text-slate-700 group-hover:text-indigo-400/50 transition-colors" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect><line x1="7" y1="2" x2="7" y2="22"></line><line x1="17" y1="2" x2="17" y2="22"></line><line x1="2" y1="12" x2="22" y2="12"></line></svg>
              <!-- Bounding Box Visual Overlay -->
              <div class="absolute inset-[25%_35%_20%_30%] border-2 border-emerald-400 bg-emerald-500/10 rounded flex items-start p-1">
                <span class="bg-emerald-500 text-slate-950 text-[9px] font-bold px-1 rounded font-mono">AoDai 98%</span>
              </div>
            </div>

            <!-- Score Badge Top Right -->
            <div class="absolute top-2 right-2 px-2 py-0.5 rounded bg-emerald-500/90 text-slate-950 text-[11px] font-bold font-mono shadow">
              98.4% MATCH
            </div>

            <!-- Video Timestamp Bottom Left -->
            <div class="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-slate-900/80 backdrop-blur-sm text-slate-200 text-[10px] font-mono border border-slate-700/50">
              01:24:15.200 (Frame #12,450)
            </div>
          </div>

          <!-- Card Content / Metadata -->
          <div class="p-3">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-mono font-semibold text-indigo-300 truncate" title="L01_V003_CAM_SAIGON">L01_V003_CAM_SAIGON</span>
              <span class="text-[10px] text-slate-400 font-mono">FPS: 30.0</span>
            </div>

            <!-- Action Buttons Row -->
            <div class="flex items-center justify-between gap-2 pt-2 border-t border-slate-700/50">
              <button class="cursor-pointer flex-1 py-1.5 px-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded text-xs font-medium flex items-center justify-center gap-1 transition-all">
                <svg class="w-3.5 h-3.5 text-sky-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                <span>Play Clip</span>
              </button>
              
              <button class="cursor-pointer flex-1 py-1.5 px-2 bg-indigo-600/20 hover:bg-indigo-600 text-indigo-300 hover:text-white border border-indigo-500/30 rounded text-xs font-medium flex items-center justify-center gap-1 transition-all">
                <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                <span>Add to Stack</span>
              </button>
            </div>
          </div>
        </div>

        <!-- CARD 2 -->
        <div class="group relative bg-slate-800/80 hover:bg-slate-800 rounded-xl border border-slate-700/80 hover:border-indigo-500/80 overflow-hidden shadow-lg transition-all duration-200 hover:-translate-y-1">
          <div class="relative aspect-video bg-slate-950 overflow-hidden cursor-pointer">
            <div class="w-full h-full bg-gradient-to-br from-slate-900 via-indigo-950/30 to-slate-900 flex items-center justify-center relative">
              <svg class="w-12 h-12 text-slate-700 group-hover:text-indigo-400/50 transition-colors" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect><line x1="7" y1="2" x2="7" y2="22"></line><line x1="17" y1="2" x2="17" y2="22"></line><line x1="2" y1="12" x2="22" y2="12"></line></svg>
              <div class="absolute inset-[30%_20%_25%_45%] border-2 border-emerald-400 bg-emerald-500/10 rounded flex items-start p-1">
                <span class="bg-emerald-500 text-slate-950 text-[9px] font-bold px-1 rounded font-mono">Person 94%</span>
              </div>
            </div>
            <div class="absolute top-2 right-2 px-2 py-0.5 rounded bg-emerald-500/90 text-slate-950 text-[11px] font-bold font-mono shadow">
              94.1% MATCH
            </div>
            <div class="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-slate-900/80 backdrop-blur-sm text-slate-200 text-[10px] font-mono border border-slate-700/50">
              00:08:42.000 (Frame #07,820)
            </div>
          </div>
          <div class="p-3">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-mono font-semibold text-indigo-300 truncate" title="L01_V008_STREET_02">L01_V008_STREET_02</span>
              <span class="text-[10px] text-slate-400 font-mono">FPS: 25.0</span>
            </div>
            <div class="flex items-center justify-between gap-2 pt-2 border-t border-slate-700/50">
              <button class="cursor-pointer flex-1 py-1.5 px-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded text-xs font-medium flex items-center justify-center gap-1 transition-all">
                <svg class="w-3.5 h-3.5 text-sky-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                <span>Play Clip</span>
              </button>
              <button class="cursor-pointer flex-1 py-1.5 px-2 bg-indigo-600/20 hover:bg-indigo-600 text-indigo-300 hover:text-white border border-indigo-500/30 rounded text-xs font-medium flex items-center justify-center gap-1 transition-all">
                <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                <span>Add to Stack</span>
              </button>
            </div>
          </div>
        </div>

        <!-- CARD 3 (ACTIVE SELECTED STATE DEMO) -->
        <div class="group relative bg-slate-800 rounded-xl border-2 border-emerald-500 overflow-hidden shadow-lg shadow-emerald-500/10 transition-all duration-200">
          <div class="relative aspect-video bg-slate-950 overflow-hidden cursor-pointer">
            <div class="w-full h-full bg-gradient-to-br from-slate-900 via-indigo-950/50 to-slate-900 flex items-center justify-center relative">
              <svg class="w-12 h-12 text-slate-700 group-hover:text-indigo-400/50 transition-colors" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect><line x1="7" y1="2" x2="7" y2="22"></line><line x1="17" y1="2" x2="17" y2="22"></line><line x1="2" y1="12" x2="22" y2="12"></line></svg>
            </div>
            <!-- Added Stack Badge Overlay -->
            <div class="absolute top-2 left-2 px-2 py-0.5 rounded bg-emerald-500 text-slate-950 text-[10px] font-bold font-mono flex items-center gap-1">
              <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"></polyline></svg>
              <span>IN STACK (#1)</span>
            </div>
            <div class="absolute top-2 right-2 px-2 py-0.5 rounded bg-emerald-500/90 text-slate-950 text-[11px] font-bold font-mono shadow">
                91.8% MATCH
            </div>
            <div class="absolute bottom-2 left-2 px-2 py-0.5 rounded bg-slate-900/80 backdrop-blur-sm text-slate-200 text-[10px] font-mono border border-slate-700/50">
              00:15:02.100 (Frame #18,012)
            </div>
          </div>
          <div class="p-3">
            <div class="flex items-center justify-between mb-2">
              <span class="text-xs font-mono font-semibold text-indigo-300 truncate" title="L02_V014_MARKET">L02_V014_MARKET</span>
              <span class="text-[10px] text-slate-400 font-mono">FPS: 30.0</span>
            </div>
            <div class="flex items-center justify-between gap-2 pt-2 border-t border-slate-700/50">
              <button class="cursor-pointer flex-1 py-1.5 px-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded text-xs font-medium flex items-center justify-center gap-1 transition-all">
                <svg class="w-3.5 h-3.5 text-sky-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                <span>Play Clip</span>
              </button>
              <button class="cursor-pointer flex-1 py-1.5 px-2 bg-emerald-600 text-white rounded text-xs font-medium flex items-center justify-center gap-1 transition-all shadow-md shadow-emerald-600/30">
                <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>
                <span>Added</span>
              </button>
            </div>
          </div>
        </div>

      </div>

      <!-- PAGINATION BAR -->
      <div class="flex items-center justify-between gap-4 mt-2 px-1 text-xs font-mono">
        <span class="text-slate-400">Showing 1 - 12 of 1,420 results</span>
        <div class="flex items-center gap-1">
          <button class="cursor-pointer px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-400 hover:text-white transition-all disabled:opacity-50">Prev</button>
          <button class="cursor-pointer px-3 py-1.5 rounded-lg bg-indigo-600 text-white font-bold transition-all">1</button>
          <button class="cursor-pointer px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 hover:bg-slate-700 transition-all">2</button>
          <button class="cursor-pointer px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 hover:bg-slate-700 transition-all">3</button>
          <span class="px-2 text-slate-500">...</span>
          <button class="cursor-pointer px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 hover:bg-slate-700 transition-all">119</button>
          <button class="cursor-pointer px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 hover:bg-slate-700 transition-all">Next</button>
        </div>
      </div>

    </div>

    <!-- RIGHT COLUMN: SUBMISSION DOCK & CONTROL PANEL (3 COLUMNS) -->
    <div class="lg:col-span-4 xl:col-span-3 flex flex-col gap-6">
      
      <!-- EVALUATION SUBMISSION CARD -->
      <section class="bg-slate-800/80 backdrop-blur-md rounded-2xl border border-indigo-500/30 p-5 shadow-2xl flex flex-col gap-4 relative overflow-hidden">
        <!-- Glowing Top Border Line -->
        <div class="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-indigo-500 via-sky-400 to-emerald-400"></div>

        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <svg class="w-5 h-5 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
            <h2 class="font-bold text-sm text-white tracking-wide uppercase font-mono">Submission Stack</h2>
          </div>
          <span class="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 text-xs font-mono">1 Item Selected</span>
        </div>

        <!-- Target Question Input Field -->
        <div>
          <label for="question-id" class="block text-xs text-slate-300 font-mono mb-1.5">Target Question ID (QA-ID):</label>
          <input 
            type="text" 
            id="question-id"
            placeholder="VD: QA_301_BATCH1" 
            class="w-full bg-slate-900 border border-slate-700 focus:border-indigo-500 rounded-lg px-3 py-2 text-xs font-mono text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
            value="QA_KIS_2026_042"
          />
        </div>

        <!-- Selected Frame Preview List -->
        <div class="space-y-2 max-h-[220px] overflow-y-auto pr-1">
          <!-- Stack Item 1 -->
          <div class="flex items-center justify-between p-2 rounded-lg bg-slate-900/80 border border-slate-700/60 text-xs font-mono">
            <div class="flex items-center gap-2 overflow-hidden">
              <div class="w-10 h-7 bg-indigo-950 rounded overflow-hidden shrink-0 border border-slate-700"></div>
              <div class="truncate">
                <p class="text-slate-200 font-semibold truncate">L02_V014_MARKET</p>
                <p class="text-[10px] text-slate-400">Frame: #18,012 | 00:15:02</p>
              </div>
            </div>
            <button class="cursor-pointer text-slate-500 hover:text-rose-400 p-1 transition-colors" title="Remove from stack">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
          </div>
        </div>

        <!-- Submit CTA Button -->
        <button class="cursor-pointer w-full py-3 px-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold rounded-xl text-xs uppercase tracking-wider font-mono shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-2 transition-all active:scale-98">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
          <span>Submit Result to Evaluation Server</span>
        </button>

        <p class="text-[10px] text-slate-400 font-mono text-center">Auto-formatted format: <code>L02_V014,18012</code></p>
      </section>

      <!-- SYSTEM API LOG & RESPONSE CONSOLE -->
      <section class="bg-slate-800/60 rounded-2xl border border-slate-700/60 p-4 font-mono text-xs flex flex-col gap-3">
        <div class="flex items-center justify-between border-b border-slate-700/50 pb-2">
          <span class="text-slate-300 font-semibold flex items-center gap-1.5">
            <svg class="w-3.5 h-3.5 text-sky-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>
            <span>Live System Console</span>
          </span>
          <span class="text-[10px] text-emerald-400">STATUS 200 OK</span>
        </div>

        <div class="bg-slate-950 rounded-lg p-3 text-[11px] leading-relaxed text-slate-300 font-mono overflow-x-auto border border-slate-800 space-y-1">
          <p class="text-slate-500">[11:24:05] Model loaded: CLIP-ViT-L/14@336px</p>
          <p class="text-indigo-400">[11:24:08] Vector Search executed in 14.2ms</p>
          <p class="text-slate-300">&gt; Query Embeddings: shape=(1, 768)</p>
          <p class="text-emerald-400">&gt; Top-1 match found in L01_V003_CAM_SAIGON (Score: 0.9842)</p>
        </div>
      </section>

    </div>

  </main>

  <!-- FOOTER -->
  <footer class="mt-auto border-t border-slate-800 py-4 px-6 text-center text-xs text-slate-500 font-mono">
    <span>AIC 2026 Challenge Platform &bull; Built with Tailwind CSS & Design System Architecture</span>
  </footer>

</body>
</html>
