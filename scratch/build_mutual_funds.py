# -*- coding: utf-8 -*-
"""
Builder for app/services/catalogue/mutual_funds.py
Covering all 11 required Indian Mutual Fund Categories:
- Nifty 50 & Broad-Market Index Funds
- Large-Cap Funds
- Flexi-Cap Funds
- Large & Mid-Cap Funds
- Mid-Cap Funds
- Small-Cap Funds
- Multi-Cap Funds
- Focused Equity Funds
- ELSS Tax-Saving Funds
- Sectoral & Thematic Funds
- Low-Risk SIP Options (Overnight, Liquid, Money Market, Short Term Debt, Banking & PSU)
"""
import sys
import os
import pprint

root_dir = r"c:\Users\shail\OneDrive\Documents\MoneyLeak"
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from scratch.generate_catalogue_modules import make_fund

funds = []

# =============================================================================
# 1. Nifty 50 and Broad-Market Index Funds (8 funds)
# =============================================================================
funds.extend([
    make_fund(
        'uti-nifty-50-index', 'UTI Nifty 50 Index Fund - Direct Plan - Growth', 'UTINIFTY',
        'Large-Cap Index Fund (Nifty 50)', 'High', 7, 159.18, '> 5 Years',
        '12.5% - 14.5% CAGR', '5Y Historical CAGR', '0.21%', 500.0,
        'Passively tracks the benchmark Nifty 50 Index with low tracking error and low expense ratio, providing low-cost diversified exposure to India’s top 50 bluechips.',
        'Core wealth compounding tracking India’s premier large-cap equity benchmark.',
        ['Low expense ratio (0.21%) and minimal tracking error against Nifty 50 Total Returns Index', 'Eliminates active fund manager risk while capturing broad Indian economic growth', 'Instant diversification across top 50 bluechip companies representing 13 economic sectors'],
        ['Subject to full equity market volatility during economic downturns', 'Cannot outperform the benchmark or take defensive cash calls during bear markets', 'Capital is market-linked and not guaranteed'],
        'UTI Mutual Fund', 'Index Fund'
    ),
    make_fund(
        'hdfc-nifty-50-index', 'HDFC Nifty 50 Index Fund - Direct Plan - Growth', 'HDFCNIFTY',
        'Large-Cap Index Fund (Nifty 50)', 'High', 7, 24.85, '> 5 Years',
        '12.5% - 14.5% CAGR', '5Y Historical CAGR', '0.20%', 100.0,
        'Low-cost index fund tracking India’s flagship Nifty 50 index with high liquidity, tight cash drag management, and minimal tracking error.',
        'Systematic low-cost investment into India’s top 50 companies with flexible SIP starting at Rs 100.',
        ['Ultra-low expense ratio (0.20%) minimizing compounding drag over 10-20 year horizons', 'Backing and risk management scale of HDFC Asset Management Company', 'Daily transparency: portfolio composition exactly mirrors the official NSE Nifty 50 index'],
        ['No downside protection: value declines proportionately when the Nifty 50 index falls', 'Index concentration: top 5 stocks account for approximately 35% of total fund weight', 'Subject to equity market cycle risks'],
        'HDFC Mutual Fund', 'Index Fund'
    ),
    make_fund(
        'icici-pru-nifty-next-50', 'ICICI Prudential Nifty Next 50 Index Fund - Direct Plan - Growth', 'ICICINEXT50',
        'Large & Mid-Cap Index Fund (Nifty Next 50)', 'High', 8, 64.20, '> 5 Years',
        '14.0% - 17.0% CAGR', '5Y Historical CAGR', '0.30%', 100.0,
        'Passively tracks the Nifty Next 50 Index (companies ranked 51-100 by market cap), capturing potential future Nifty 50 leaders with higher growth potential.',
        'Aggressive large-cap growth: investing in emerging market leaders across fast-growing industries.',
        ['High growth potential: historically delivered higher long-term compounding than Nifty 50', 'Sectoral diversity: higher exposure to capital goods, chemicals, and consumer discretionaries', 'Systematic pipeline: holds the next batch of companies poised for promotion into the Nifty 50'],
        ['Higher volatility and deeper drawdowns during market corrections than the Nifty 50 index', 'Higher tracking error historically than core Nifty 50 funds', 'Requires a minimum 5-7 year patient investment horizon'],
        'ICICI Prudential Mutual Fund', 'Index Fund'
    ),
    make_fund(
        'motilal-nifty-500-index', 'Motilal Oswal Nifty 500 Index Fund - Direct Plan - Growth', 'MOTILAL500',
        'Broad-Market Index Fund (Nifty 500)', 'High', 8, 28.50, '> 5 Years',
        '13.5% - 16.5% CAGR', '5Y Historical CAGR', '0.38%', 500.0,
        'India’s first broad-market index fund replicating the Nifty 500 Index, capturing over 95% of total free-float market capitalization across Large, Mid, and Small-cap stocks.',
        'Complete one-stop exposure to the entire Indian listed corporate universe in a single fund.',
        ['Total market representation: holds large-caps (72%), mid-caps (18%), and small-caps (10%)', 'Automatically rebalances weights as companies grow across market-cap spectrums', 'Eliminates category-switching dilemmas by investing in the entire economic landscape'],
        ['Higher volatility than pure large-cap index funds due to small-cap allocation', 'Higher number of holdings (500 stocks) results in modest tracking differences', 'Subject to overall equity market corrections'],
        'Motilal Oswal Mutual Fund', 'Index Fund'
    ),
    make_fund(
        'uti-bse-sensex-index', 'UTI BSE Sensex Index Fund - Direct Plan - Growth', 'UTISENSEX',
        'Large-Cap Index Fund (BSE Sensex)', 'High', 7, 218.40, '> 5 Years',
        '12.5% - 14.5% CAGR', '5Y Historical CAGR', '0.20%', 500.0,
        'Passively tracks the 30 mega-cap leaders of the historic BSE Sensex, India’s oldest and most renowned equity market barometer.',
        'Conservative large-cap compounding in India’s 30 largest established industrial and financial giants.',
        ['Extreme bluechip focus: concentrated in India’s top 30 corporate champions with proven moats', 'Ultra-low expense ratio (0.20%) and reliable tracking efficiency', 'Decades of multi-economic-cycle compounding history'],
        ['High single-stock and sector concentration (banking & financials weight exceeds 38%)', 'Excludes mid-cap and emerging sector exposure found in broader indices', 'Returns are purely market-linked with no capital protection'],
        'UTI Mutual Fund', 'Index Fund'
    ),
    make_fund(
        'navi-nifty-50-index', 'Navi Nifty 50 Index Fund - Direct Plan - Growth', 'NAVINIFTY',
        'Large-Cap Index Fund (Nifty 50)', 'High', 7, 18.90, '> 5 Years',
        '12.5% - 14.5% CAGR', '5Y Historical CAGR', '0.06%', 10.0,
        'Disruptive digital-first index fund offering one of the lowest expense ratios in the Indian mutual fund industry (0.06%), tracking the Nifty 50 Index.',
        'Ultra-low-cost passive compounding maximizing net investor returns through fintech efficiency.',
        ['Industry-lowest expense ratio (0.06%) preserving virtually 100% of benchmark returns for investors', 'Accessible systematic investing with micro-SIPs starting from just Rs 10', '100% automated algorithmic index replication minimizing manual portfolio intervention'],
        ['Newer track record compared to veteran fund houses like UTI or HDFC', 'Tracking difference during periods of high cash inflow or volatile index reconstitution', 'Subject to full market drawdown risk'],
        'Navi Mutual Fund', 'Index Fund'
    ),
    make_fund(
        'nippon-nifty-smallcap-250', 'Nippon India Nifty Smallcap 250 Index Fund - Direct Plan - Growth', 'NIPPSMALL250',
        'Small-Cap Index Fund (Nifty Smallcap 250)', 'High', 9, 32.10, '> 7 Years',
        '16.0% - 21.0% CAGR', '5Y Historical CAGR', '0.35%', 100.0,
        'Passively replicates the Nifty Smallcap 250 Index (companies ranked 251-500 by market capitalization), capturing high-growth emerging businesses across sunrise sectors.',
        'High-octane capital appreciation through systematic exposure to India’s fast-growing small-cap companies.',
        ['Unbiased algorithmic rule-based exposure to 250 emerging small-cap companies', 'Eliminates active fund manager bias, cash holding drag, and stock selection risk', 'Direct participation in India’s manufacturing, specialty chemicals, and capital goods boom'],
        ['Extremely high volatility: small-cap indices can experience drawdowns exceeding 30-40% during bear markets', 'Liquidity constraints in underlying small-cap stocks can cause tracking error during sharp selloffs', 'Strictly requires an aggressive risk appetite and a 7+ year horizon'],
        'Nippon India Mutual Fund', 'Index Fund'
    ),
    make_fund(
        'motilal-nifty-midcap-150', 'Motilal Oswal Nifty Midcap 150 Index Fund - Direct Plan - Growth', 'MOTILALMID150',
        'Mid-Cap Index Fund (Nifty Midcap 150)', 'High', 8, 38.40, '> 5 Years',
        '15.0% - 18.5% CAGR', '5Y Historical CAGR', '0.32%', 500.0,
        'Passively tracks the Nifty Midcap 150 Index (companies ranked 101-250 by market capitalization), targeting the sweet spot of Indian corporate growth.',
        'High-growth compounding in established mid-sized businesses with scalable business models.',
        ['Captures the dynamic mid-cap sweet spot: higher growth than large-caps with better liquidity than small-caps', 'Diversified portfolio across 150 mid-tier market leaders with low expense ratio', 'Rule-based semi-annual rebalancing automatically promotes winners'],
        ['Higher volatility and sharper corrections during economic slowdowns than the Nifty 50', 'Tracking error can expand during volatile market reconstitution phases', 'Requires patient 5+ year holding period to ride out cyclical dips'],
        'Motilal Oswal Mutual Fund', 'Index Fund'
    )
])

# =============================================================================
# 2. Large-Cap Funds (10 funds across 10 AMCs)
# =============================================================================
funds.extend([
    make_fund(
        'sbi-bluechip-fund', 'SBI Bluechip Fund - Direct Plan - Growth', 'SBIBLUE',
        'Large-Cap Active Mutual Fund', 'High', 7, 96.99, '> 5 Years',
        '12.5% - 15.0% CAGR', '5Y Historical CAGR', '0.84%', 500.0,
        'Flagship active large-cap fund of India’s largest fund house, investing in established bluechip leaders with robust competitive moats and strong balance sheets.',
        'Consistent long-term capital growth backed by SBI Mutual Fund’s institutional research depth.',
        ['Disciplined active stock selection across top 100 bluechip market leaders', 'Robust risk management dampening portfolio drawdowns during broad market corrections', 'Backed by India’s largest asset manager with vast institutional research capabilities'],
        ['Higher expense ratio than passive index funds (0.84% vs 0.20%)', 'May underperform during sharp speculative market momentum rallies', 'Full equity market risk applies'],
        'SBI Mutual Fund', 'Large Cap Fund'
    ),
    make_fund(
        'hdfc-top-100-fund', 'HDFC Top 100 Fund - Direct Plan - Growth', 'HDFCTOP100',
        'Large-Cap Active Mutual Fund', 'High', 7, 1142.50, '> 5 Years',
        '13.0% - 15.5% CAGR', '5Y Historical CAGR', '1.05%', 100.0,
        'One of India’s oldest and most prestigious large-cap funds with over 25-year track record, investing in large, established businesses with strong pricing power.',
        'Long-term core compounding in India’s leading corporate champions.',
        ['Proven 25+ year track record navigating multiple economic and market cycles', 'High active conviction in cash-flow-generating industrial and financial leaders', 'Disciplined value-conscious investment framework avoiding overhyped speculative bubbles'],
        ['Higher expense ratio (1.05%) requires consistent active alpha generation to beat index', 'Conservative cash calls during bull runs can lead to temporary benchmark underperformance', 'Subject to equity market drawdowns'],
        'HDFC Mutual Fund', 'Large Cap Fund'
    ),
    make_fund(
        'icici-pru-bluechip-fund', 'ICICI Prudential Bluechip Fund - Direct Plan - Growth', 'ICICIBLUE',
        'Large-Cap Active Mutual Fund', 'High', 7, 108.60, '> 5 Years',
        '13.5% - 16.0% CAGR', '5Y Historical CAGR', '0.90%', 100.0,
        'Flagship large-cap fund managing over Rs 55,000 Crore, focusing on industry leaders with strong balance sheets and counter-cyclical sector rotation.',
        'High-quality large-cap equity growth with dynamic counter-cyclical valuation discipline.',
        ['Exceptional track record of downside protection during severe market crashes', 'Disciplined counter-cyclical investment approach buying quality leaders during market pessimism', 'High portfolio liquidity enabling swift risk mitigation'],
        ['Large asset size (AUM > Rs 55,000 Cr) makes rapid portfolio changes more gradual', 'Underperforms during hyper-momentum speculative small/mid-cap rallies', 'Equity capital is not protected'],
        'ICICI Prudential Mutual Fund', 'Large Cap Fund'
    ),
    make_fund(
        'kotak-bluechip-fund', 'Kotak Bluechip Fund - Direct Plan - Growth', 'KOTAKBLUE',
        'Large-Cap Active Mutual Fund', 'High', 7, 542.80, '> 5 Years',
        '13.0% - 15.5% CAGR', '5Y Historical CAGR', '0.74%', 100.0,
        'Quality-oriented large-cap fund focusing on sustainable growth, high Return on Capital Employed (RoCE), and corporate governance excellence.',
        'Disciplined compounding through financially disciplined corporate leaders with low leverage.',
        ['Relentless focus on corporate governance excellence and clean accounting standards', 'Competitive expense ratio (0.74%) among active large-cap peers', 'Consistent quartile performance across 3-year and 5-year rolling return windows'],
        ['Quality-bias portfolio may lag during low-quality cyclical commodity rallies', 'Active risk: returns depend on fund management team stock selection', 'Market-linked returns with no capital guarantee'],
        'Kotak Mahindra Mutual Fund', 'Large Cap Fund'
    ),
    make_fund(
        'nippon-india-large-cap', 'Nippon India Large Cap Fund - Direct Plan - Growth', 'NIPPLARGE',
        'Large-Cap Active Mutual Fund', 'High', 7, 88.50, '> 5 Years',
        '14.0% - 16.5% CAGR', '5Y Historical CAGR', '0.82%', 100.0,
        'Top-performing active large-cap fund utilizing active growth-at-reasonable-price (GARP) strategy and opportunistic cyclical sector allocation.',
        'Alpha generation through active sector rotation and undervalued large-cap leaders.',
        ['Consistently ranked in the top quartile of large-cap active funds over recent multi-year periods', 'Dynamic sector allocation successfully capitalizing on domestic manufacturing and banking upcycles', 'Disciplined profit-taking in fully valued large-cap names'],
        ['Higher portfolio turnover and active beta than conservative peers like ICICI Bluechip', 'Subject to sector rotation timing risk', 'Market volatility applies'],
        'Nippon India Mutual Fund', 'Large Cap Fund'
    ),
    make_fund(
        'axis-bluechip-fund', 'Axis Bluechip Fund - Direct Plan - Growth', 'AXISBLUE',
        'Large-Cap Active Mutual Fund', 'High', 7, 58.20, '> 5 Years',
        '11.0% - 13.5% CAGR', '5Y Historical CAGR', '0.78%', 100.0,
        'Quality growth fund prioritizing secular growth franchises with high return on equity (RoE) and low financial leverage.',
        'High-quality compounding in secular growth leaders across consumption, technology, and private banking.',
        ['Zero tolerance for corporate governance compromises or high debt balance sheets', 'Historically lower portfolio volatility and defensive resilience during economic shocks', 'High concentration in top-tier private sector franchises'],
        ['Underperformed significantly during recent high-inflation and commodity value-stock rallies', 'Premium valuation of portfolio holdings elevates risk during P/E multiple contraction cycles', 'Equity market risk applies'],
        'Axis Mutual Fund', 'Large Cap Fund'
    ),
    make_fund(
        'uti-mastershare-fund', 'UTI Large Cap Fund (Mastershare) - Direct Plan - Growth', 'UTIMASTERSHARE',
        'Large-Cap Active Mutual Fund', 'High', 7, 268.40, '> 5 Years',
        '12.5% - 15.0% CAGR', '5Y Historical CAGR', '0.88%', 500.0,
        'India’s first equity mutual fund launched in 1986, with nearly 40 years of wealth creation history focusing on competitive franchise moats.',
        'Enduring long-term equity compounding through India’s oldest mutual fund scheme.',
        ['Unmatched 38-year operational heritage navigating every post-liberalization economic cycle', 'Growth-at-reasonable-price (GARP) framework maintaining high sector diversification', 'Consistent dividend and growth track record through multi-decade market history'],
        ['Moderate active alpha generation compared to high-conviction peers', 'Active management fee overhead compared to passive index funds', 'Market-linked returns'],
        'UTI Mutual Fund', 'Large Cap Fund'
    ),
    make_fund(
        'mirae-asset-large-cap', 'Mirae Asset Large Cap Fund - Direct Plan - Growth', 'MIRAELARGE',
        'Large-Cap Active Mutual Fund', 'High', 7, 118.90, '> 5 Years',
        '13.0% - 15.5% CAGR', '5Y Historical CAGR', '0.54%', 500.0,
        'High-conviction large-cap fund combining bottom-up stock picking with macro sector trends, maintaining a competitive direct plan expense ratio (0.54%).',
        'Core bluechip equity compounding with one of the most competitive expense ratios among active funds.',
        ['Extremely competitive direct expense ratio (0.54%) providing structural compounding advantage', 'Disciplined focus on market leaders with sustainable competitive advantages and high operating cash flows', 'Rigorous risk management limiting single-stock exposure risks'],
        ['AUM growth has moderated active nimbleness compared to its early years', 'Active risk relative to the Nifty 100 benchmark', 'Equity market drawdown risk applies'],
        'Mirae Asset Mutual Fund', 'Large Cap Fund'
    ),
    make_fund(
        'canara-robeco-bluechip', 'Canara Robeco Bluechip Equity Fund - Direct Plan - Growth', 'CANARABLUE',
        'Large-Cap Active Mutual Fund', 'High', 7, 62.40, '> 5 Years',
        '13.5% - 16.0% CAGR', '5Y Historical CAGR', '0.52%', 100.0,
        'Consistent top-performing large-cap fund celebrated for low portfolio volatility, high Sharpe ratio, and steady alpha generation through quality stock picking.',
        'Low-volatility large-cap compounding with exceptional risk-adjusted return track record.',
        ['Consistently superior risk-adjusted returns with lower standard deviation than category average', 'Lowest expense ratio in active large-cap category (0.52%)', 'High-quality portfolio construct with zero exposure to speculative high-debt businesses'],
        ['Conservative approach may lag during aggressive low-quality speculative momentum rallies', 'Active fund manager dependency for stock selection', 'Full equity market risks apply'],
        'Canara Robeco Mutual Fund', 'Large Cap Fund'
    ),
    make_fund(
        'dsp-top-100-equity', 'DSP Top 100 Equity Fund - Direct Plan - Growth', 'DSPTOP100',
        'Large-Cap Active Mutual Fund', 'High', 7, 412.30, '> 5 Years',
        '12.0% - 14.5% CAGR', '5Y Historical CAGR', '0.98%', 100.0,
        'Veteran large-cap fund backed by global investment processes, investing in top 100 companies with resilient business models and sound balance sheets.',
        'High-quality large-cap equity growth backed by institutional research discipline.',
        ['Over 20-year operational history with disciplined investment philosophy', 'Focus on companies capable of sustaining high returns on invested capital across cycles', 'Transparent portfolio disclosures and robust risk management framework'],
        ['Higher expense ratio (0.98%) than low-cost peers', 'Periodic benchmark underperformance during rapid market shifts', 'Market-linked equity risk applies'],
        'DSP Mutual Fund', 'Large Cap Fund'
    )
])

# =============================================================================
# 3. Flexi-Cap Funds (5 funds)
# =============================================================================
funds.extend([
    make_fund(
        'parag-parikh-flexi-cap', 'Parag Parikh Flexi Cap Fund - Direct Plan - Growth', 'PPFCF',
        'Flexi-Cap Mutual Fund', 'High', 8, 88.97, '> 5 Years',
        '16.0% - 19.5% CAGR', '5Y Historical CAGR', '0.63%', 500.0,
        'Flagship value-oriented flexi-cap fund known for high cash holdings during expensive markets, low churn, and disciplined value investing across market caps.',
        'Long-term value compounding with benchmark-beating risk-adjusted returns and cash allocation discipline.',
        ['Exceptional long-term track record outperforming benchmarks with lower standard deviation', 'High manager skin-in-the-game: fund managers and AMC staff invest substantial personal wealth in the fund', 'Low portfolio turnover and patient buy-and-hold philosophy minimizing friction costs'],
        ['RBI foreign investment limit caps prevent adding new direct overseas equity positions (Alphabet, Microsoft)', 'High cash allocations during bull markets can lead to temporary short-term underperformance', 'Subject to equity market cycle risks'],
        'PPFAS Mutual Fund', 'Flexi Cap Fund'
    ),
    make_fund(
        'hdfc-flexi-cap-fund', 'HDFC Flexi Cap Fund - Direct Plan - Growth', 'HDFCFLEXI',
        'Flexi-Cap Mutual Fund', 'High', 8, 1920.40, '> 5 Years',
        '16.5% - 20.0% CAGR', '5Y Historical CAGR', '0.85%', 100.0,
        'One of India’s largest mutual funds managing over Rs 65,000 Crore, executed with a contrarian, cash-flow-driven value investment philosophy across market caps.',
        'Aggressive multi-cap growth capitalizing on Indian manufacturing, power, banking, and public sector turnaround.',
        ['Phenomenal multi-year turnaround performance delivering industry-leading alpha', 'Deep research-driven contrarian investment approach buying unloved quality assets at bargain valuations', 'Experienced fund management team with decades of market cycle expertise'],
        ['Very large AUM (Rs 65,000+ Cr) limits meaningful small-cap allocations due to liquidity impact', 'Contrarian value calls can take 1-3 years to play out, testing investor patience', 'High equity market volatility'],
        'HDFC Mutual Fund', 'Flexi Cap Fund'
    ),
    make_fund(
        'kotak-flexi-cap-fund', 'Kotak Flexi Cap Fund - Direct Plan - Growth', 'KOTAKFLEXI',
        'Flexi-Cap Mutual Fund', 'High', 8, 84.10, '> 5 Years',
        '14.0% - 16.5% CAGR', '5Y Historical CAGR', '0.61%', 100.0,
        'India’s pioneering flexi-cap fund managing over Rs 45,000 Crore, utilizing a disciplined large-cap-oriented flexi-cap approach with tactical mid-cap exposure.',
        'Steady core wealth creation with moderate volatility and competitive expense ratio (0.61%).',
        ['Established 15+ year wealth creation track record with high institutional investor participation', 'Disciplined large-cap anchor (~70%) providing stability while mid-caps (~25%) provide alpha', 'Low expense ratio compared to active category average'],
        ['Conservative posture means it may lag more aggressive mid/small-cap heavy flexi-cap funds during speculative rallies', 'Large fund size limits agility in niche high-growth micro-caps', 'Equity market drawdowns apply'],
        'Kotak Mahindra Mutual Fund', 'Flexi Cap Fund'
    ),
    make_fund(
        'jm-flexi-cap-fund', 'JM Flexi Cap Fund - Direct Plan - Growth', 'JMFLEXI',
        'Flexi-Cap Mutual Fund', 'High', 8, 128.50, '> 5 Years',
        '18.0% - 22.5% CAGR', '5Y Historical CAGR', '0.45%', 100.0,
        'High-conviction dynamic flexi-cap fund known for agile sector rotation, momentum stock selection, and exceptional multi-year alpha generation.',
        'High-growth wealth acceleration through agile sector rotation and high-conviction mid-cap alpha.',
        ['Top-ranked flexi-cap fund delivering exceptional 1-year, 3-year, and 5-year rolling returns', 'Extremely low expense ratio (0.45%) for an active high-alpha fund', 'Nimble fund size allowing quick capitalization on emerging sector themes (defense, power, capital goods)'],
        ['Higher portfolio turnover and aggressive active momentum strategy elevate drawdown risk in bear markets', 'Higher standard deviation and beta than conservative flexi-caps like Parag Parikh', 'Requires aggressive risk tolerance and 5+ year horizon'],
        'JM Financial Mutual Fund', 'Flexi Cap Fund'
    ),
    make_fund(
        'canara-robeco-flexi-cap', 'Canara Robeco Flexi Cap Fund - Direct Plan - Growth', 'CANARAFLEXI',
        'Flexi-Cap Mutual Fund', 'High', 8, 342.10, '> 5 Years',
        '14.5% - 17.5% CAGR', '5Y Historical CAGR', '0.53%', 100.0,
        'Consistent and steady flexi-cap fund with proven track record of superior risk-adjusted returns, low drawdowns, and high Sharpe ratio.',
        'Consistent wealth accumulation with smooth return profile and below-average downside volatility.',
        ['Consistently superior risk-adjusted metrics with lower drawdowns during market corrections', 'Balanced allocation across large-caps (65-70%) and growth-oriented mid-caps (25-30%)', 'Competitive expense ratio (0.53%) maximizing investor net returns'],
        ['Conservative posture may lag during speculative low-quality momentum surges', 'Active stock-picking dependency', 'Market-linked returns'],
        'Canara Robeco Mutual Fund', 'Flexi Cap Fund'
    )
])

# =============================================================================
# 4. Large and Mid-Cap Funds (4 funds)
# =============================================================================
funds.extend([
    make_fund(
        'mirae-asset-large-midcap', 'Mirae Asset Large & Midcap Fund - Direct Plan - Growth', 'MIRAELARGEMID',
        'Large & Mid-Cap Mutual Fund', 'High', 8, 163.09, '> 5 Years',
        '15.0% - 18.0% CAGR', '5Y Historical CAGR', '0.58%', 500.0,
        'Flagship mandate mandatorily investing minimum 35% in large-caps and 35% in mid-caps, capturing steady bluechips alongside fast-growing mid-tier winners.',
        'Optimal blend of large-cap resilience and mid-cap alpha in a single disciplined mandate.',
        ['Mandatory regulatory asset allocation ensures genuine exposure to both large-caps (35%+) and mid-caps (35%+)', 'Superb multi-year performance track record with high institutional investor trust', 'Competitive direct plan expense ratio (0.58%)'],
        ['Higher volatility than pure large-cap funds due to mandatory 35%+ mid-cap allocation', 'Large AUM size requires disciplined liquidity management across mid-cap picks', 'Equity capital is not guaranteed'],
        'Mirae Asset Mutual Fund', 'Large & Mid Cap Fund'
    ),
    make_fund(
        'kotak-equity-opportunities', 'Kotak Equity Opportunities Fund - Direct Plan - Growth', 'KOTAKEQUITYOPP',
        'Large & Mid-Cap Mutual Fund', 'High', 8, 362.40, '> 5 Years',
        '15.5% - 18.5% CAGR', '5Y Historical CAGR', '0.56%', 100.0,
        'Top-performing large & mid-cap fund utilizing a growth-at-reasonable-price philosophy to identify industry leaders and emerging challengers across sectors.',
        'High-conviction growth opportunities across India’s top 250 companies.',
        ['Consistently outperforms category benchmark with disciplined risk controls', 'Skilled at identifying mid-sized companies on the verge of becoming large-cap industry leaders', 'High portfolio liquidity and low expense ratio (0.56%)'],
        ['Mid-cap sleeve introduces sharper drawdowns during market corrections', 'Active fund manager decision risk', 'Market-linked returns'],
        'Kotak Mahindra Mutual Fund', 'Large & Mid Cap Fund'
    ),
    make_fund(
        'hdfc-large-mid-cap', 'HDFC Large and Mid Cap Fund - Direct Plan - Growth', 'HDFCLARGEMID',
        'Large & Mid-Cap Mutual Fund', 'High', 8, 318.50, '> 5 Years',
        '16.0% - 19.0% CAGR', '5Y Historical CAGR', '0.82%', 100.0,
        'Aggressive large & mid-cap wealth builder combining cash-flow compounding with value-oriented mid-cap cyclicals (industrials, auto ancillaries, power).',
        'High capital growth through domestic manufacturing, defense, and capital goods upcycles.',
        ['Top-decile performance across 3-year and 5-year periods driven by high-conviction thematic picks', 'Strong research depth of HDFC AMC in evaluating mid-sized manufacturing leaders', 'Balanced portfolio structure preventing single-stock overconcentration'],
        ['Higher beta and drawdowns than pure large-cap index funds during bear markets', 'Higher portfolio turnover during sector rotation phases', 'Equity market volatility applies'],
        'HDFC Mutual Fund', 'Large & Mid Cap Fund'
    ),
    make_fund(
        'sbi-large-midcap-fund', 'SBI Large & Midcap Fund - Direct Plan - Growth', 'SBILARGEMID',
        'Large & Mid-Cap Mutual Fund', 'High', 8, 542.10, '> 5 Years',
        '14.5% - 17.5% CAGR', '5Y Historical CAGR', '0.84%', 500.0,
        'Conservative large & mid-cap fund backed by SBI Mutual Fund’s institutional research, prioritizing fundamentally sound businesses with strong earnings visibility.',
        'Balanced multi-cap growth with institutional downside risk management.',
        ['Steady performance across market cycles with disciplined stock weight limits', 'Access to unlisted and pre-IPO opportunities through institutional allocation mandates', 'Strong credit and governance filters avoiding high-debt mid-caps'],
        ['May lag aggressive momentum funds during speculative mid-cap market phases', 'Higher expense ratio (0.84%) than low-cost peers', 'Subject to equity market cycle risks'],
        'SBI Mutual Fund', 'Large & Mid Cap Fund'
    )
])

# =============================================================================
# 5. Mid-Cap Funds (4 funds)
# =============================================================================
funds.extend([
    make_fund(
        'hdfc-mid-cap-opportunities', 'HDFC Mid-Cap Opportunities Fund - Direct Plan - Growth', 'HDFCMIDCAP',
        'Mid-Cap Active Mutual Fund', 'High', 8, 184.20, '> 5 Years',
        '18.0% - 22.0% CAGR', '5Y Historical CAGR', '0.74%', 100.0,
        'India’s largest mid-cap mutual fund managing over Rs 70,000 Crore, focused on identifying companies poised to transition from mid-sized players into mega-cap champions.',
        'High-growth capital compounding in emerging market leaders across domestic manufacturing and consumer themes.',
        ['Phenomenal long-term compounding track record over 15+ years through multiple market cycles', 'Highly diversified portfolio of over 60 mid-cap leaders limiting single-stock shock risk', 'Experienced fund management team with unmatched access to corporate promoters and management'],
        ['Mid-cap stocks are significantly more volatile than large-caps with larger drawdowns in corrections', 'Huge fund size (AUM > Rs 70,000 Cr) makes rapid liquidity exits challenging in illiquid names', 'Requires a minimum 5-7 year patient investment horizon'],
        'HDFC Mutual Fund', 'Mid Cap Fund'
    ),
    make_fund(
        'motilal-oswal-midcap', 'Motilal Oswal Midcap Fund - Direct Plan - Growth', 'MOTILALMID',
        'Mid-Cap Active Mutual Fund', 'High', 8, 112.40, '> 5 Years',
        '20.0% - 25.0% CAGR', '5Y Historical CAGR', '0.66%', 500.0,
        'High-conviction, concentrated mid-cap fund operating on the "Quality, Growth, Longevity, and Price" (QGLP) framework with a tight portfolio of 25-30 high-growth stocks.',
        'Aggressive capital acceleration through focused high-conviction mid-cap market leaders.',
        ['Industry-leading 3-year and 5-year alpha generation consistently topping mid-cap performance charts', 'High-conviction portfolio: top 10 holdings account for over 50% of the fund, maximizing winners', 'Strict adherence to QGLP framework ensuring high RoE and strong secular earnings growth'],
        ['High portfolio concentration elevates stock-specific volatility if a key holding misses earnings', 'Higher standard deviation and beta than diversified mid-cap peers', 'Strictly suitable for aggressive investors with 7+ year horizon'],
        'Motilal Oswal Mutual Fund', 'Mid Cap Fund'
    ),
    make_fund(
        'kotak-emerging-equity', 'Kotak Emerging Equity Fund - Direct Plan - Growth', 'KOTAKEMERGING',
        'Mid-Cap Active Mutual Fund', 'High', 8, 126.80, '> 5 Years',
        '17.5% - 21.0% CAGR', '5Y Historical CAGR', '0.62%', 100.0,
        'Pioneering mid-cap fund managing over Rs 45,000 Crore, renowned for disciplined bottom-up stock picking, strong balance sheet filters, and multi-year holding periods.',
        'Disciplined mid-cap wealth creation avoiding speculative high-debt turnaround stories.',
        ['Benchmark of governance discipline in mid-cap investing with zero tolerance for accounting red flags', 'Consistent upper-quartile performance across rolling 5-year investment horizons', 'High return on capital employed (RoCE) across portfolio holdings'],
        ['Substantial AUM size limits agile trading in smaller mid-cap names', 'Conservative posture may lag during low-quality speculative mid-cap rallies', 'Full equity market drawdown risk'],
        'Kotak Mahindra Mutual Fund', 'Mid Cap Fund'
    ),
    make_fund(
        'nippon-india-growth-fund', 'Nippon India Growth Fund - Direct Plan - Growth', 'NIPPGROWTH',
        'Mid-Cap Active Mutual Fund', 'High', 8, 3840.50, '> 5 Years',
        '18.5% - 22.5% CAGR', '5Y Historical CAGR', '0.84%', 100.0,
        'One of India’s oldest mid-cap funds with a legendary 28-year wealth creation history, specializing in aggressive growth-oriented mid-tier companies.',
        'Aggressive capital growth participating in India’s emerging industrial, retail, and tech leaders.',
        ['Spectacular 28-year wealth creation track record compounding investor capital at over 20% since inception', 'Dynamic stock selection identifying sunrise sector leaders before institutional discovery', 'High active share ensuring genuine differentiated alpha from the benchmark'],
        ['Higher portfolio volatility and sharper drawdowns during market corrections', 'Higher expense ratio (0.84%) than low-cost peers', 'Requires minimum 5-7 year holding patience'],
        'Nippon India Mutual Fund', 'Mid Cap Fund'
    )
])

# =============================================================================
# 6. Small-Cap Funds (4 funds)
# =============================================================================
funds.extend([
    make_fund(
        'nippon-india-small-cap', 'Nippon India Small Cap Fund - Direct Plan - Growth', 'NIPPSMALL',
        'Small-Cap Active Mutual Fund', 'High', 9, 178.60, '> 7 Years',
        '20.0% - 25.5% CAGR', '5Y Historical CAGR', '0.67%', 100.0,
        'India’s largest and most celebrated small-cap fund managing over Rs 55,000 Crore, highly diversified across 180+ small-cap stocks with extraordinary alpha generation.',
        'Aggressive multi-year wealth compounding in India’s emerging niche market champions.',
        ['Legendary wealth compounding track record delivering over 25% CAGR across multi-year cycles', 'Extreme diversification (180+ stocks) effectively eliminates single-stock blow-up risk in small-caps', 'Exceptional research team conducting deep ground-level channel checks on emerging companies'],
        ['Small-cap stocks carry substantial market risk and can correct 30-50% during broad bear markets', 'Very large fund size has led to periodic restrictions on lump-sum subscriptions', 'Strictly requires aggressive risk tolerance and a 7+ year horizon'],
        'Nippon India Mutual Fund', 'Small Cap Fund'
    ),
    make_fund(
        'quant-small-cap-fund', 'Quant Small Cap Fund - Direct Plan - Growth', 'QUANTSMALL',
        'Small-Cap Active Mutual Fund', 'High', 9, 298.40, '> 7 Years',
        '22.0% - 28.0% CAGR', '5Y Historical CAGR', '0.64%', 500.0,
        'Dynamic quant-driven small-cap fund utilizing predictive analytics, VLRT framework (Valuation, Liquidity, Risk, Timing), and agile active sector rotation.',
        'High-velocity capital appreciation through algorithmic predictive momentum and active risk management.',
        ['Phenomenal top-ranked multi-year performance delivering market-beating returns', 'Algorithmic VLRT framework ruthlessly cuts losing positions and rides momentum winners', 'Willingness to take contrarian cash or large-cap defensive positions during small-cap market peaks'],
        ['High portfolio turnover (> 100%) and aggressive trading approach elevate strategy execution risk', 'Subject to extreme volatility during sudden market regime changes and illiquidity shocks', 'Requires high risk appetite and emotional fortitude during drawdowns'],
        'Quant Mutual Fund', 'Small Cap Fund'
    ),
    make_fund(
        'sbi-small-cap-fund', 'SBI Small Cap Fund - Direct Plan - Growth', 'SBISMALL',
        'Small-Cap Active Mutual Fund', 'High', 9, 186.20, '> 7 Years',
        '18.0% - 22.5% CAGR', '5Y Historical CAGR', '0.68%', 500.0,
        'Pioneering small-cap fund renowned for high institutional discipline, rigorous promoter governance screening, and disciplined capacity-capping to protect existing investors.',
        'High-quality small-cap compounding focusing on clean corporate governance and sustainable business models.',
        ['Benchmark governance screening avoiding high-debt, promoter-pledged, or dubious small-caps', 'Superior downside protection during past severe small-cap bear markets', 'Track record of responsible capacity management pausing fresh lump sums when valuations become stretched'],
        ['Lump-sum investments frequently restricted to prevent dilution of fund alpha', 'Conservative stock selection may lag during low-quality speculative small-cap bubbles', 'Small-cap market volatility applies'],
        'SBI Mutual Fund', 'Small Cap Fund'
    ),
    make_fund(
        'tata-small-cap-fund', 'Tata Small Cap Fund - Direct Plan - Growth', 'TATASMALL',
        'Small-Cap Active Mutual Fund', 'High', 9, 44.80, '> 7 Years',
        '19.5% - 24.5% CAGR', '5Y Historical CAGR', '0.48%', 100.0,
        'High-growth small-cap fund backed by the Tata Group, celebrated for clean corporate governance, bottom-up stock picking, and one of the lowest expense ratios in the small-cap category (0.48%).',
        'Rapid capital compounding in emerging sunrise sector leaders with attractive expense ratio.',
        ['Lowest expense ratio in the active small-cap category (0.48%) maximizing net investor returns', 'Disciplined focus on companies with high return on capital and expanding operating cash flows', 'Nimble fund size allowing opportunistic entry into niche high-growth emerging companies'],
        ['High volatility and drawdown potential inherent in the small-cap asset class', 'Shorter track record than veteran peers like Nippon India', 'Strictly requires a 7+ year investment horizon'],
        'Tata Mutual Fund', 'Small Cap Fund'
    )
])

# =============================================================================
# 7. Multi-Cap Funds (3 funds)
# =============================================================================
funds.extend([
    make_fund(
        'nippon-india-multi-cap', 'Nippon India Multi Cap Fund - Direct Plan - Growth', 'NIPPMULTI',
        'Multi-Cap Mutual Fund', 'High', 8, 312.40, '> 5 Years',
        '17.0% - 21.0% CAGR', '5Y Historical CAGR', '0.82%', 100.0,
        'True multi-cap fund strictly complying with SEBI mandate: minimum 25% in Large-Caps, 25% in Mid-Caps, and 25% in Small-Caps at all times, capturing all-weather growth.',
        'Guaranteed all-cap diversification across India’s corporate landscape in a single fund.',
        ['Mandatory regulatory diversification ensures permanent exposure to high-growth small-caps (25%) and mid-caps (25%) alongside large-cap anchors (25%)', 'Consistently outperforms category benchmark through superior small and mid-cap stock selection', 'Eliminates fund manager bias to flee into large-caps during market rallies'],
        ['Higher volatility than flexi-cap funds due to permanent mandatory 50% allocation to mid and small caps', 'Cannot shift fully to defensive cash or large-caps during severe market downturns', 'Requires a 5-7 year holding horizon'],
        'Nippon India Mutual Fund', 'Multi Cap Fund'
    ),
    make_fund(
        'icici-pru-multi-cap', 'ICICI Prudential Multi-Cap Fund - Direct Plan - Growth', 'ICICIMULTI',
        'Multi-Cap Mutual Fund', 'High', 8, 742.10, '> 5 Years',
        '16.0% - 19.5% CAGR', '5Y Historical CAGR', '0.88%', 100.0,
        'Veteran multi-cap fund managing mandatory 25-25-25 allocation with counter-cyclical valuation discipline, ensuring balanced market-cap exposure with downside protection.',
        'All-weather capital growth combining bluechip stability with high-potential mid and small-cap winners.',
        ['Balanced risk profile supported by ICICI Prudential’s rigorous risk management framework', 'Proven ability to protect capital better than pure mid/small cap funds during corrections', 'Disciplined rebalancing maintaining optimal 25-25-25 weights'],
        ['Higher expense ratio (0.88%) than passive multi-cap index options', 'Mandatory 25% small-cap rule increases baseline portfolio volatility', 'Equity market risk applies'],
        'ICICI Prudential Mutual Fund', 'Multi Cap Fund'
    ),
    make_fund(
        'mahindra-manulife-multi-cap', 'Mahindra Manulife Multi Cap Fund - Direct Plan - Growth', 'MAHINDRAMULTI',
        'Multi-Cap Mutual Fund', 'High', 8, 42.60, '> 5 Years',
        '18.0% - 22.0% CAGR', '5Y Historical CAGR', '0.44%', 500.0,
        'Top-performing agile multi-cap fund combining domestic rural insight of the Mahindra Group with global investment expertise of Manulife, delivering top-quartile alpha.',
        'High-growth multi-cap compounding with exceptionally competitive expense ratio (0.44%).',
        ['Industry-lowest direct expense ratio (0.44%) in the multi-cap category', 'Top-decile performance across 3-year and 5-year rolling return windows', 'Unique research synergy combining rural Indian economic insights with global asset allocation discipline'],
        ['Smaller AUM size than veteran peers like Nippon India', 'Mandatory 25% small-cap rule induces drawdowns during bear markets', 'Requires 5+ year investment horizon'],
        'Mahindra Manulife Mutual Fund', 'Multi Cap Fund'
    )
])

# =============================================================================
# 8. Focused Equity Funds (3 funds)
# =============================================================================
funds.extend([
    make_fund(
        'sbi-focused-equity-fund', 'SBI Focused Equity Fund - Direct Plan - Growth', 'SBIFOCUSED',
        'Focused Equity Mutual Fund', 'High', 8, 342.50, '> 5 Years',
        '14.5% - 17.5% CAGR', '5Y Historical CAGR', '0.68%', 500.0,
        'High-conviction equity fund restricted by mandate to maximum 30 stocks, backing highest-conviction ideas across market capitalizations.',
        'Outsized capital growth through concentrated exposure to top 30 corporate winners.',
        ['High active share: focuses capital only on the fund manager’s 25-30 highest-conviction stock ideas', 'Proven multi-year track record with significant alpha generation over diversified benchmarks', 'Flexibility to invest across large, mid, and small-cap stocks without rigid category constraints'],
        ['Higher portfolio concentration risk: underperformance of 2-3 key holdings directly impacts fund returns', 'Higher volatility and tracking error relative to diversified equity funds', 'Requires high risk tolerance and 5+ year horizon'],
        'SBI Mutual Fund', 'Focused Fund'
    ),
    make_fund(
        'icici-pru-focused-equity', 'ICICI Prudential Focused Equity Fund - Direct Plan - Growth', 'ICICIFOCUSED',
        'Focused Equity Mutual Fund', 'High', 8, 78.40, '> 5 Years',
        '15.5% - 18.5% CAGR', '5Y Historical CAGR', '0.72%', 100.0,
        'Concentrated fund investing in up to 30 high-conviction companies, blending value-oriented large-caps with growth mid-caps using counter-cyclical framework.',
        'High-conviction stock picking with institutional valuation discipline.',
        ['Strong track record of picking unloved market leaders and riding multi-year re-ratings', 'Concentrated portfolio (maximum 30 stocks) eliminates low-conviction portfolio dilution', 'Rigorous risk management capping single-stock and sector exposure limits'],
        ['Concentration risk: stock-specific misjudgments have larger portfolio return impact', 'May lag broad-market rallies if concentrated sectors are out of institutional favor', 'Equity market volatility applies'],
        'ICICI Prudential Mutual Fund', 'Focused Fund'
    ),
    make_fund(
        '360-one-focused-equity', '360 ONE Focused Equity Fund - Direct Plan - Growth', '360ONEFOCUSED',
        'Focused Equity Mutual Fund', 'High', 8, 54.20, '> 5 Years',
        '17.0% - 21.0% CAGR', '5Y Historical CAGR', '0.78%', 1000.0,
        'High-alpha focused fund (formerly IIFL Focused Equity) investing in maximum 30 high-quality growth businesses with high return on equity (RoE) and pricing power.',
        'Aggressive capital compounding through focused allocation to superior business franchises.',
        ['Consistently ranked in the top quartile of focused funds over multi-year periods', 'Strict proprietary screening for high free cash flow generation, moat durability, and low leverage', 'High active conviction with disciplined profit-taking'],
        ['High portfolio concentration elevates volatility during market corrections', 'Higher minimum investment requirement (Rs 1,000)', 'Requires patient 5+ year holding period'],
        '360 ONE Asset Management', 'Focused Fund'
    )
])

# =============================================================================
# 9. ELSS Tax-Saving Funds (4 funds)
# =============================================================================
funds.extend([
    make_fund(
        'mirae-asset-elss-tax-saver', 'Mirae Asset ELSS Tax Saver Fund - Direct Plan - Growth', 'MIRELSS',
        'ELSS Tax-Saving Mutual Fund', 'High', 8, 48.90, '3 - 5 Years',
        '15.5% - 18.5% CAGR', '5Y Historical CAGR', '0.59%', 500.0,
        'Flagship tax-saving scheme qualifying for Section 80C statutory deduction up to Rs 1.5 Lakh, with mandatory 3-year lock-in and high-conviction growth portfolio.',
        'Statutory tax saving under Section 80C combined with long-term equity compounding at shortest lock-in (3 years).',
        ['Statutory tax deduction up to Rs 1.5 Lakh under Section 80C saving up to Rs 46,800 in annual income tax', 'Shortest lock-in period (3 years) among all Section 80C investments (PPF has 15 years, Tax FDs have 5 years)', 'Enforced holding period prevents emotional panic-selling during temporary market dips'],
        ['Mandatory 3-year statutory lock-in: funds cannot be redeemed under any circumstances during lock-in', 'Every individual SIP installment is locked in for 3 full years from its respective investment date', 'Equity market risk applies: capital is not guaranteed'],
        'Mirae Asset Mutual Fund', 'ELSS'
    ),
    make_fund(
        'quant-elss-tax-saver', 'Quant ELSS Tax Saver Fund - Direct Plan - Growth', 'QUANTELSS',
        'ELSS Tax-Saving Mutual Fund', 'High', 8, 412.50, '3 - 5 Years',
        '20.0% - 25.0% CAGR', '5Y Historical CAGR', '0.77%', 500.0,
        'Top-performing tax-saving fund utilizing quantitative momentum and VLRT framework to generate market-beating returns alongside Section 80C tax benefits.',
        'High-velocity capital appreciation and Section 80C tax deductions through algorithmic momentum investing.',
        ['Highest historical 3-year and 5-year returns in the entire ELSS tax-saver category', 'Algorithmic risk framework actively shifts sector exposure into momentum winners', 'Qualifies for Section 80C tax deduction up to Rs 1.5 Lakh per financial year'],
        ['Mandatory 3-year statutory lock-in restricts liquidity completely', 'Higher portfolio volatility and aggressive turnover strategy require high risk tolerance', 'Returns are purely market-linked with no capital protection'],
        'Quant Mutual Fund', 'ELSS'
    ),
    make_fund(
        'parag-parikh-elss-tax-saver', 'Parag Parikh ELSS Tax Saver Fund - Direct Plan - Growth', 'PPELSS',
        'ELSS Tax-Saving Mutual Fund', 'High', 8, 32.40, '3 - 5 Years',
        '16.0% - 19.0% CAGR', '5Y Historical CAGR', '0.62%', 500.0,
        'Value-oriented tax-saving fund applying PPFAS’s disciplined value framework to Section 80C investments, prioritizing quality businesses at fair valuations.',
        'Tax-advantaged value investing with low portfolio turnover and high manager alignment.',
        ['Section 80C tax deduction combined with conservative, patient value investing philosophy', 'Low portfolio turnover and high manager skin-in-the-game', 'Disciplined risk management limiting drawdown depth during market corrections'],
        ['Mandatory 3-year statutory lock-in applies to all units and SIP installments', 'Value-bias may lag high-momentum aggressive funds during speculative bull runs', 'Capital is market-linked and not guaranteed'],
        'PPFAS Mutual Fund', 'ELSS'
    ),
    make_fund(
        'bandhan-elss-tax-saver', 'Bandhan ELSS Tax Saver Fund - Direct Plan - Growth', 'BANDHANELSS',
        'ELSS Tax-Saving Mutual Fund', 'High', 8, 148.20, '3 - 5 Years',
        '15.0% - 18.0% CAGR', '5Y Historical CAGR', '0.65%', 500.0,
        'Established tax-saver fund (formerly IDFC Tax Advantage) with consistent long-term track record of growth-at-reasonable-price investing across market caps.',
        'Section 80C tax deduction with balanced multi-cap equity exposure.',
        ['Consistent multi-decade track record of steady alpha generation and disciplined risk controls', 'Balanced allocation across large, mid, and small-cap growth champions', 'Section 80C tax deduction up to Rs 1.5 Lakh with 3-year lock-in'],
        ['Mandatory 3-year lock-in restricts capital accessibility', 'Active stock selection risk', 'Subject to equity market drawdowns'],
        'Bandhan Mutual Fund', 'ELSS'
    )
])

# =============================================================================
# 10. Sectoral and Thematic Funds (6 funds)
# =============================================================================
funds.extend([
    make_fund(
        'icici-pru-banking-financial', 'ICICI Prudential Banking & Financial Services Fund - Direct Plan - Growth', 'ICICIBANKING',
        'Sectoral Fund (Banking & Financials)', 'High', 8, 134.50, '> 5 Years',
        '14.5% - 17.5% CAGR', '5Y Historical CAGR', '0.88%', 100.0,
        'Sectoral fund investing exclusively in banks, NBFCs, insurance, asset management, and fintech companies driving India’s financial credit growth.',
        'Targeted participation in India’s expanding credit-to-GDP ratio, digital payments, and capital markets expansion.',
        ['Pure-play exposure to the backbone of Indian economic growth: banking and credit expansion', 'Captures value across banks, NBFCs, life/general insurance, and wealth platforms', 'Experienced sector specialist fund management team with deep banking insights'],
        ['High sector concentration risk: underperforms heavily during banking NPA cycles or RBI monetary tightening', 'Not suitable as a standalone portfolio; requires diversification with other sectors', 'High volatility during financial sector market corrections'],
        'ICICI Prudential Mutual Fund', 'Sectoral Fund'
    ),
    make_fund(
        'tata-digital-india-fund', 'Tata Digital India Fund - Direct Plan - Growth', 'TATADIGITAL',
        'Sectoral Fund (Information Technology)', 'High', 8, 52.80, '> 5 Years',
        '15.5% - 19.5% CAGR', '5Y Historical CAGR', '0.84%', 100.0,
        'Sectoral fund investing in Indian IT services, software products, cloud engineering, cybersecurity, and digital platforms benefiting from global tech spend.',
        'Targeted investment in global enterprise digital transformation, cloud migration, and Generative AI spending.',
        ['Focused portfolio of India’s premier global IT services exporters (TCS, Infosys, HCL Tech, LTIMindtree)', 'Strong historical cash generation and high dividend yield characteristics of underlying tech companies', 'Currency hedge: benefits from US Dollar appreciation against the Indian Rupee'],
        ['High sector concentration risk: heavily dependent on US and European corporate tech budgets', 'Extended consolidation periods during global tech discretionary spend slowdowns', 'Elevated volatility requires aggressive risk tolerance and 5+ year horizon'],
        'Tata Mutual Fund', 'Sectoral Fund'
    ),
    make_fund(
        'nippon-india-pharma-fund', 'Nippon India Pharma Fund - Direct Plan - Growth', 'NIPPPHARMA',
        'Sectoral Fund (Pharma & Healthcare)', 'High', 8, 512.40, '> 5 Years',
        '15.0% - 18.5% CAGR', '5Y Historical CAGR', '0.94%', 100.0,
        'India’s largest and oldest healthcare sector fund, investing across pharmaceutical formulations, active pharmaceutical ingredients (APIs), hospitals, and diagnostics.',
        'Targeted compounding in domestic chronic healthcare demand, global generic formulations, and booming hospital infrastructure.',
        ['Comprehensive healthcare coverage spanning global pharma exporters and domestic hospital chains (Apollo, Max)', 'Defensive non-cyclical demand: healthcare consumption continues regardless of macroeconomic slowdowns', 'Strong tailwind from global CDMO China+1 supply chain diversification'],
        ['Sector concentration risk: vulnerable to US FDA regulatory inspection crackdowns on manufacturing plants', 'Price control regulations (DPCO/NLEM) by the Indian government on essential medicines', 'Higher expense ratio (0.94%) typical of specialized sectoral funds'],
        'Nippon India Mutual Fund', 'Sectoral Fund'
    ),
    make_fund(
        'icici-pru-infrastructure', 'ICICI Prudential Infrastructure Fund - Direct Plan - Growth', 'ICICIINFRA',
        'Thematic Fund (Infrastructure & Capital Goods)', 'High', 8, 184.60, '> 5 Years',
        '18.0% - 22.5% CAGR', '5Y Historical CAGR', '0.98%', 100.0,
        'Top-performing thematic fund investing in companies benefiting from national infrastructure creation: construction, power transmission, capital goods, cement, and defense.',
        'Capitalizing on the multi-lakh-crore National Infrastructure Pipeline and private corporate capex revival.',
        ['Direct beneficiary of record central government budgetary capex allocations in railways, roads, and power', 'Superb multi-year alpha generation outperforming broader equity benchmarks', 'Captures manufacturing, engineering, and logistics leaders in a single focused theme'],
        ['High thematic concentration risk: underperforms during periods of government fiscal austerity or capex slowdowns', 'High sensitivity to raw material input costs (steel, cement, energy)', 'High beta and cyclical drawdown risk during market downturns'],
        'ICICI Prudential Mutual Fund', 'Thematic Fund'
    ),
    make_fund(
        'sbi-automotive-mobility', 'SBI Automotive Opportunities Fund - Direct Plan - Growth', 'SBIAUTO',
        'Thematic Fund (Automotive & EV Mobility)', 'High', 8, 14.80, '> 5 Years',
        '16.0% - 20.0% CAGR', '5Y Historical CAGR', '0.92%', 500.0,
        'Specialized thematic fund investing across the automotive value chain: passenger vehicles, two-wheelers, auto ancillaries, EV battery ecosystems, and autonomous software.',
        'Targeted participation in India’s automotive premiumization, electric vehicle transition, and global auto component exports.',
        ['Pure-play exposure to India’s booming automotive industry and global tier-1 component outsourcing', 'Captures the EV technology transition spanning batteries, power electronics, and lightweighting', 'Backed by SBI Mutual Fund’s sector research depth'],
        ['Thematic concentration: automotive sector is inherently cyclical and sensitive to interest rates and fuel prices', 'Newer fund track record with limited historical cycle testing', 'High stock price volatility during auto sales volume moderation'],
        'SBI Mutual Fund', 'Thematic Fund'
    ),
    make_fund(
        'hdfc-manufacturing-fund', 'HDFC Manufacturing Fund - Direct Plan - Growth', 'HDFCMFG',
        'Thematic Fund (Make in India & Manufacturing)', 'High', 8, 12.40, '> 5 Years',
        '16.5% - 20.5% CAGR', '5Y Historical CAGR', '0.89%', 100.0,
        'Thematic fund capturing the "Make in India" manufacturing resurgence driven by PLI schemes, global supply chain de-risking, and industrial capex upcycles.',
        'Targeted investment in electronics manufacturing, defense production, industrial automation, and chemical exports.',
        ['Aligned directly with government Production Linked Incentive (PLI) schemes driving domestic manufacturing', 'Broad industrial exposure spanning defense, electronics EMS, heavy machinery, and specialty materials', 'Diversified across market-caps from established conglomerates to emerging mid-cap exporters'],
        ['Thematic concentration risk: dependent on sustained private and public manufacturing capex momentum', 'Execution delays in industrial plant commissioning and global export trade tariff barriers', 'High volatility during industrial sector pullbacks'],
        'HDFC Mutual Fund', 'Thematic Fund'
    )
])

# =============================================================================
# 11. Lower-Risk-Oriented SIP Options (7 funds: Overnight, Liquid, Debt)
# =============================================================================
funds.extend([
    make_fund(
        'sbi-overnight-fund', 'SBI Overnight Fund - Direct Plan - Growth', 'SBIOVERNIGHT',
        'Overnight Mutual Fund (Ultra-Low Risk)', 'Low', 1, 4120.50, '< 1 Year',
        '6.25% - 6.75% p.a.', 'Current Yield / 1Y', '0.10%', 500.0,
        'Ultra-low-risk mutual fund investing exclusively in overnight securities with 1-day maturity (TREPS and reverse repo), completely eliminating credit and interest rate duration risk.',
        'Safe parking of emergency funds or surplus business capital with daily liquidity and zero interest rate risk.',
        ['Lowest possible risk in the mutual fund industry: invests only in 1-day maturity sovereign collateralized paper', 'Zero exit load and instant T+1 redemption without any lock-in', 'Completely immune to mark-to-market interest rate fluctuations or corporate bond defaults'],
        ['Returns track RBI overnight repo rate and will moderate during interest rate easing cycles', 'Not designed for long-term wealth compounding; intended strictly for short-term parking', 'Mutual funds are not bank deposits; no DICGC insurance applies'],
        'SBI Mutual Fund', 'Overnight Fund'
    ),
    make_fund(
        'hdfc-overnight-fund', 'HDFC Overnight Fund - Direct Plan - Growth', 'HDFCOVERNIGHT',
        'Overnight Mutual Fund (Ultra-Low Risk)', 'Low', 1, 3540.80, '< 1 Year',
        '6.25% - 6.75% p.a.', 'Current Yield / 1Y', '0.10%', 100.0,
        'Safest category mutual fund holding 1-day maturity overnight instruments collateralized by government securities, offering predictable yields and daily accessibility.',
        'Ideal short-term cash management and systematic transfer plan (STP) source into equity funds.',
        ['Extreme safety: 100% portfolio matures every single business day', 'Seamless systematic transfer plan (STP) feeder into HDFC equity and flexi-cap funds', 'Low expense ratio (0.10%) and zero credit default exposure'],
        ['Low returns relative to long-term inflation and equity compounding', 'Debt fund taxation applies at personal income slab rates', 'No statutory deposit guarantee'],
        'HDFC Mutual Fund', 'Overnight Fund'
    ),
    make_fund(
        'icici-pru-liquid-fund', 'ICICI Prudential Liquid Fund - Direct Plan - Growth', 'ICICILIQUID',
        'Liquid Mutual Fund (Low Risk)', 'Low', 1, 385.40, '1 - 3 Months',
        '6.75% - 7.25% p.a.', 'Current Yield / 1Y', '0.15%', 100.0,
        'Premier liquid fund investing in high-quality money market instruments (T-Bills, Commercial Papers, Certificates of Deposit) with maximum 91-day maturity.',
        'High safety, low volatility emergency cash reserve with instant redemption facility up to Rs 50,000.',
        ['Instant Redemption Facility: access up to Rs 50,000 or 90% of value instantly within minutes 24x7', 'Pristine portfolio credit quality consisting exclusively of sovereign and AAA/A1+ rated papers', 'Higher return than traditional bank savings accounts with minimal interest rate volatility'],
        ['Graduated exit load applies for redemptions within the first 7 days of investment', 'Yields fluctuate with prevailing short-term money market liquidity conditions', 'Capital is not insured by DICGC'],
        'ICICI Prudential Mutual Fund', 'Liquid Fund'
    ),
    make_fund(
        'aditya-birla-liquid-fund', 'Aditya Birla Sun Life Liquid Fund - Direct Plan - Growth', 'ABSLIQUID',
        'Liquid Mutual Fund (Low Risk)', 'Low', 1, 412.80, '1 - 3 Months',
        '6.75% - 7.25% p.a.', 'Current Yield / 1Y', '0.18%', 500.0,
        'Established liquid fund managing institutional liquidity with rigorous credit screening, low duration, and predictable short-term capital preservation.',
        'Short-term liquidity management and corporate cash parking with high credit safety.',
        ['Over 20-year track record of impeccable credit safety and liquidity management', 'Portfolio weighted average maturity strictly restricted below 60 days to prevent interest rate shocks', 'Ideal tool for holding short-term goal capital and tax reserves'],
        ['Graded exit load applies only if redeemed within 7 days of allotment', 'Returns are taxable at personal income slab rates', 'Capital is market-linked'],
        'Aditya Birla Sun Life Mutual Fund', 'Liquid Fund'
    ),
    make_fund(
        'hdfc-money-market-fund', 'HDFC Money Market Fund - Direct Plan - Growth', 'HDFCMONEYMKT',
        'Money Market Mutual Fund (Low Risk)', 'Low', 2, 54.80, '3 - 12 Months',
        '7.10% - 7.60% p.a.', 'Current Yield / 1Y', '0.19%', 100.0,
        'Low-risk debt fund investing in money market securities with maturity up to 1 year, offering higher yields than liquid funds while maintaining strong credit quality.',
        'Parking capital for 3 to 12 months with superior yields and negligible credit risk.',
        ['Higher yield potential than overnight and liquid funds by capturing up to 1-year money market spreads', 'Invests exclusively in top-tier A1+ commercial papers and certificate of deposits', 'Zero exit load: complete liquidity to withdraw or switch funds anytime without penalty'],
        ['Modest mark-to-market sensitivity to sharp short-term interest rate spikes', 'Taxed at investor’s personal income slab rate', 'Not guaranteed by the government'],
        'HDFC Mutual Fund', 'Money Market Fund'
    ),
    make_fund(
        'hdfc-short-term-debt', 'HDFC Short Term Debt Fund - Direct Plan - Growth', 'HDFCSHORTTERM',
        'Short Duration Debt Mutual Fund (Low-Moderate Risk)', 'Low', 2, 32.10, '1 - 3 Years',
        '7.25% - 7.85% p.a.', 'Current Yield / 3Y', '0.35%', 100.0,
        'High-quality short duration debt fund investing in corporate bonds and government securities with Macaulay duration of 1 to 3 years, optimizing accrual yields with low interest rate risk.',
        'Predictable capital accrual for 1 to 3 year financial goals with superior credit quality.',
        ['Over 85% of portfolio invested in sovereign G-Secs and AAA rated public/private corporate bonds', 'Captures attractive corporate bond spreads with controlled interest rate duration risk', 'Zero exit load providing high flexibility for medium-term capital deployment'],
        ['Subject to moderate mark-to-market duration fluctuations if RBI raises benchmark policy rates', 'Gains taxed at personal income slab rates under current tax laws', 'Mutual fund returns are not contractual or guaranteed'],
        'HDFC Mutual Fund', 'Short Duration Fund'
    ),
    make_fund(
        'sbi-banking-psu-debt', 'SBI Banking & PSU Debt Fund - Direct Plan - Growth', 'SBIBANKPSU',
        'Banking and PSU Debt Mutual Fund (Low Risk)', 'Low', 2, 3450.20, '1 - 3 Years',
        '7.15% - 7.70% p.a.', 'Current Yield / 3Y', '0.32%', 500.0,
        'High-safety debt fund mandatorily investing minimum 80% in debt instruments of scheduled commercial banks, Public Sector Undertakings (PSUs), and Public Financial Institutions.',
        'High credit safety: near-sovereign credit quality for conservative fixed-income investors.',
        ['Exceptional credit safety: invests in sovereign G-Secs, SBI, HDFC Bank, NABARD, REC, and PFC bonds', 'Near-zero credit default risk supported by systemic quasi-sovereign standing of issuers', 'Highly liquid underlying bond portfolio with low expense ratio (0.32%)'],
        ['Moderate duration sensitivity: fund NAV fluctuates with medium-term bond yield movements', 'Taxed at personal slab rate without indexation benefits', 'Returns are market-linked and not guaranteed'],
        'SBI Mutual Fund', 'Banking & PSU Fund'
    )
])

print(f"Added all mutual fund categories! Total funds: {len(funds)}")

# Save mutual funds catalogue
funds_path = os.path.join(root_dir, 'app', 'services', 'catalogue', 'mutual_funds.py')
with open(funds_path, 'w', encoding='utf-8') as f:
    f.write('"""\nExpanded Indian Mutual Funds Catalogue across 11 Major Categories for MoneyLeak.\n')
    f.write('Covering Index Funds, Large Cap, Flexi Cap, Large & Mid, Mid Cap, Small Cap, Multi Cap,\n')
    f.write('Focused, ELSS, Sectoral/Thematic, and Low-Risk Overnight/Liquid/Debt Funds.\n"""\n')
    f.write('from typing import Dict, Any, List\n\n')
    f.write('MUTUAL_FUNDS_CATALOGUE: List[Dict[str, Any]] = ')
    pprint.pprint(funds, stream=f, indent=4, width=120)
    f.write('\n')

print(f"Successfully wrote {funds_path} with {len(funds)} mutual funds.")
