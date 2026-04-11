---
name: vnstock
description: Skill truy xuất và phân tích dữ liệu chứng khoán Việt Nam sử dụng thư viện vnstock. Hỗ trợ lấy giá cổ phiếu, báo cáo tài chính, thông tin công ty, bảng giá realtime, quỹ đầu tư, giá vàng, tỷ giá ngoại tệ, và các chỉ số thị trường.
user-invocable: true
metadata:
  openclaw:
    requires:
      bins: ["python"]
---

# 📈 Vnstock - Skill Phân Tích Chứng Khoán Việt Nam

## Objective

Giúp người dùng truy xuất và phân tích dữ liệu chứng khoán Việt Nam thông qua thư viện Python **vnstock** (phiên bản miễn phí, mã nguồn mở). Skill này cho phép agent tự động viết và chạy code Python để lấy dữ liệu thị trường, phân tích tài chính, và trả lời các câu hỏi liên quan đến cổ phiếu VN.

## Yêu cầu hệ thống

Trước khi thực thi, đảm bảo vnstock đã được cài đặt:

```bash
pip install -U vnstock
```

Nếu chưa cài, hãy chạy lệnh trên trước.

**Phiên bản đã test**: vnstock 3.5.0 (Python 3.13)

### Xác thực người dùng (tùy chọn)

Đăng ký API key miễn phí tại https://vnstocks.com/login để tăng giới hạn sử dụng:
- **Guest** (không đăng ký): 20 req/phút, tối đa 4 kỳ BCTC
- **Community** (miễn phí): 60 req/phút, tối đa 8 kỳ BCTC
- **Sponsor** (trả phí): 3-5x req, không quảng cáo, đầy đủ BCTC

```python
from vnstock import register_user
register_user()                              # Nhập key theo hướng dẫn
# hoặc
register_user(api_key='vnstock_59d75e4db410c618ddce96b2e2698951')     # Nhập trực tiếp
```

---

## 📚 Tổng Quan API

### Thư viện chính: `vnstock`
- **Miễn phí & mã nguồn mở**
- **Dữ liệu**: Cổ phiếu, chỉ số, quỹ, trái phiếu, FX, vàng, crypto
- **Nguồn dữ liệu**:Ưu tiên `KBS` (ổn định nhất, khuyến nghị mặc định) hoặc `VCI` (fallback hoặc khi cần dữ liệu ICB chi tiết).
- **CƠ CHẾ FALLBACK**: Hầu hết các module hỗ trợ ưu tiên `KBS`. Nếu `KBS` không trả về dữ liệu hoặc gặp lỗi, hệ thống sẽ tự động thử lại với `VCI`.
- ⚠️ **KHÔNG sử dụng nguồn TCBS** (đã deprecated)

### Các class chính

| Class | Mô tả | Import |
|-------|--------|--------|
| `Vnstock` | Giao diện chính, khởi tạo tất cả module | `from vnstock import Vnstock` |
| `Listing` | Danh sách mã CK, lọc theo sàn/ngành/chỉ số | `from vnstock import Listing` |
| `Quote` | Giá lịch sử OHLCV, intraday, price depth | `from vnstock import Quote` |
| `Company` | Thông tin công ty, cổ đông, ban lãnh đạo | `from vnstock import Company` |
| `Finance` | Báo cáo tài chính, chỉ số tài chính | `from vnstock import Finance` |
| `Trading` | Bảng giá realtime | `from vnstock import Trading` |
| `Fund` | Quỹ đầu tư mở (Fmarket) | `from vnstock import Fund` |

### Tiện ích thêm

| Hàm | Mô tả | Import |
|-----|--------|--------|
| `sjc_gold_price()` | Giá vàng SJC | `from vnstock.explorer.misc import sjc_gold_price` |
| `btmc_goldprice()` | Giá vàng Bảo Tín Minh Châu | `from vnstock.explorer.misc import btmc_goldprice` |
| `vcb_exchange_rate()` | Tỷ giá ngoại tệ Vietcombank | `from vnstock.explorer.misc import vcb_exchange_rate` |

---

## 📖 Hướng Dẫn Chi Tiết Từng API

### 1. Listing API - Danh Sách Chứng Khoán

```python
from vnstock import Listing

listing = Listing(source='KBS')  # hoặc 'VCI'

# Tất cả mã chứng khoán
df = listing.all_symbols(to_df=True)          # DataFrame (symbol, organ_name)
symbols = listing.all_symbols(to_df=False)    # List[str]

# Lọc theo sàn giao dịch
hose = listing.symbols_by_exchange(exchange='HOSE', to_df=True)
hnx = listing.symbols_by_exchange(exchange='HNX', to_df=True)
upcom = listing.symbols_by_exchange(exchange='UPCOM', to_df=True)

# Lọc theo ngành
industries = listing.symbols_by_industries(to_df=True)  # Tất cả ngành
banking = listing.symbols_by_industries(industry_name='Ngân hàng', to_df=True)

# Lọc theo chỉ số
vn30 = listing.symbols_by_group(group_name='VN30', to_df=True)   # DataFrame
vn30_series = listing.symbols_by_group(group_name='VN30', to_df=False)  # Pandas Series
vn30_list = vn30_series.tolist()  # Chuyển sang list Python
vn100 = listing.symbols_by_group(group_name='VN100', to_df=True)
# ⚠️ LƯU Ý: to_df=False trả về Pandas Series, KHÔNG phải list. Dùng .tolist() để chuyển.
# Các chỉ số: VN30, VN100, VNMID, VNSML, VNALL, VNSI, HNX30
# Chỉ số ngành: VNIT, VNIND, VNCONS, VNCOND, VNHEAL, VNENE, VNUTI, VNREAL, VNFIN, VNMAT
# Chỉ số đầu tư: VNDIAMOND, VNFINLEAD, VNFINSELECT
# Chỉ số liên sàn: VNX50, VNXALL

# Phân loại ICB (Chỉ VCI)
icb = listing.industries_icb()

# Futures, Bonds, Warrants
futures = listing.all_future_indices()
gov_bonds = listing.all_government_bonds()
warrants = listing.all_covered_warrant()
corp_bonds = listing.all_bonds()

# ETF (chỉ KBS)
etf = listing.all_etf()

# Tất cả chỉ số thị trường và nhóm chỉ số
all_indices = listing.all_indices()
hose_indices = listing.indices_by_group('HOSE Indices') # Sector Indices, Investment Indices, VNX Indices
```

### 2. Quote API - Giá Cổ Phiếu

```python
from vnstock import Quote

quote = Quote(symbol='VCB', source='KBS')  # hoặc không cần source (mặc định VCI)

# === Giá lịch sử OHLCV ===

# Cách 1: Theo khoảng thời gian (start/end)
df = quote.history(start='2024-01-01', end='2024-12-31', interval='1D')

# Cách 2: Lookback với length
df = quote.history(length='1M', interval='1D')    # 1 tháng gần nhất
df = quote.history(length='3M', interval='1D')    # 3 tháng (1 quý)
df = quote.history(length='6M', interval='1D')    # 6 tháng
df = quote.history(length='1Y', interval='1D')    # 1 năm
df = quote.history(length='2Y', interval='1D')    # 2 năm
df = quote.history(length=150, interval='1D')     # 150 ngày
df = quote.history(length='100b', interval='1D')  # 100 nến (bars)
df = quote.history(length='1Q', interval='1D')    # 1 quý

# Intervals hỗ trợ:
# '1m'/'m'  = 1 phút | '5m' = 5 phút | '15m' = 15 phút | '30m' = 30 phút
# '1H'/'h'  = 1 giờ  | '1D'/'d' = 1 ngày | '1W'/'w' = 1 tuần | '1M'/'M' = 1 tháng
# ⚠️ Case-sensitive: 'M' = tháng (viết hoa), 'm' = phút (viết thường)

# KBS: Thêm cột value
df = quote.history(length='1M', interval='1D', get_all=True)
# Columns: ['time', 'open', 'high', 'low', 'close', 'volume', 'value']

# === Dữ liệu khớp lệnh trong ngày (Intraday) ===
intraday = quote.intraday(page_size=100)
# Columns: ['time', 'price', 'volume', 'match_type', 'id']
# match_type: 'buy' hoặc 'sell'

# === Price Depth (chỉ VCI) ===
# quote_vci = Quote(symbol='VCB', source='VCI')
# depth = quote_vci.price_depth()
# Columns: ['price', 'volume', 'buy_volume', 'sell_volume']
```

### 3. Company API - Thông Tin Công Ty

```python
from vnstock import Company

company = Company(source='KBS', symbol='VCB')

# Thông tin tổng quan (KBS: 30 columns, VCI: 10 columns)
overview = company.overview()

# Cổ đông lớn
shareholders = company.shareholders()
# KBS: ['name', 'update_date', 'shares_owned', 'ownership_percentage']
# VCI: ['share_holder', 'quantity', 'share_own_percent', ...]

# Ban lãnh đạo
officers = company.officers()
# ['from_date', 'position', 'name', 'position_en', 'owner_code']

# Công ty con (Chỉ KBS tốt nhất)
subsidiaries = company.subsidiaries()

# Công ty liên kết
affiliate = company.affiliate()

# Tin tức
news = company.news()
# KBS: ['head', 'article_id', 'publish_time', 'url']

# Sự kiện (cổ tức, phát hành cổ phiếu...)
events = company.events()
# ⚠️ KBS có thể rỗng, nên dùng VCI cho events (tự động fallback nếu dùng CLI helper)

# === Methods chỉ KBS ===
ownership = company.ownership()           # Cơ cấu cổ đông theo tỷ lệ
capital = company.capital_history()        # Lịch sử vốn điều lệ
insider = company.insider_trading()        # Giao dịch nội bộ

# === Methods chỉ VCI ===
# company_vci = Company(source='VCI', symbol='VCB')
# reports = company_vci.reports()          # Báo cáo phân tích
# trading_stats = company_vci.trading_stats()  # Thống kê giao dịch
# ratio_summary = company_vci.ratio_summary()  # Tóm tắt chỉ số tài chính
```

### 4. Finance API - Báo Cáo Tài Chính

```python
from vnstock import Finance

finance = Finance(symbol='VCB', source='KBS')

# Báo cáo kết quả kinh doanh
income = finance.income_statement(period='quarter')  # hoặc 'year'
# Shape: (~90 items, ~10 cols)
# Columns: ['item', 'item_id', 'unit', 'levels', 'row_number', '2025-Q3', ...]

# Bảng cân đối kế toán
balance = finance.balance_sheet(period='quarter')
# Shape: (~162 items)

# Báo cáo lưu chuyển tiền tệ
cashflow = finance.cash_flow(period='quarter')
# Shape: (~159 items)

# Chỉ số tài chính (PE, PB, ROE, ROA, Beta...)
ratios = finance.ratio(period='quarter')
# Shape: (~27 items)

# === Lọc dữ liệu ===
# Chỉ tiêu chính (level 1)
key_items = income[income['levels'] == 1]

# Lọc theo item_id
revenue = income[income['item_id'] == 'revenue']
net_profit = income[income['item_id'] == 'net_profit']

# === Display Mode (v3.4.0+) ===
# STD (mặc định): chỉ item + item_id
# ALL: item + item_en + item_id
# 'vi': chỉ tiếng Việt
# 'en': chỉ tiếng Anh
income_all = finance.income_statement(period='quarter', display_mode='all')

# === Mapping item_id quan trọng ===
# revenue          = Doanh thu
# gross_profit     = Lợi nhuận gộp
# operating_profit = Lợi nhuận hoạt động
# net_profit       = Lợi nhuận sau thuế
# total_assets     = Tổng tài sản
# owner_equity     = Vốn chủ sở hữu
# liabilities      = Nợ phải trả
# pe, pb, roe, roa, beta = Các chỉ số tài chính
```

### 5. Trading API - Bảng Giá Realtime

```python
from vnstock import Trading

trading = Trading(source='KBS', symbol='VCB')

# Bảng giá nhiều mã
board = trading.price_board(symbols_list=['VCB', 'ACB', 'TCB', 'BID', 'CTG'])
# KBS (29 columns): symbol, exchange, ceiling_price, floor_price, reference_price,
#   open_price, high_price, low_price, close_price, average_price,
#   volume_accumulated, total_value, price_change, percent_change,
#   bid_price_1..3, bid_vol_1..3, ask_price_1..3, ask_vol_1..3,
#   foreign_buy_volume, foreign_sell_volume

# VCI (77 columns): chi tiết hơn KBS
# trading_vci = Trading(source='VCI', symbol='VCB')
# board_vci = trading_vci.price_board(symbols_list=['VCB', 'ACB'])
```

### 6. Fund API - Quỹ Đầu Tư Mở

```python
from vnstock import Fund

fund = Fund()

# Danh sách tất cả quỹ (~58 quỹ)
all_funds = fund.listing()
# fund_type: '' (tất cả), 'STOCK', 'BOND', 'BALANCED'
stock_funds = fund.listing(fund_type='STOCK')

# Columns chính: short_name, name, fund_type, fund_owner_name,
#   management_fee, nav, nav_change_12m, nav_change_36m, ...

# Top 5 quỹ theo lợi suất 1 năm
top5 = all_funds.nlargest(5, 'nav_change_12m')
```

### 7. Dữ Liệu Bổ Sung

```python
# === Giá vàng SJC ===
from vnstock.explorer.misc import sjc_gold_price
gold = sjc_gold_price()                      # Hôm nay
gold = sjc_gold_price(date='2025-01-15')     # Ngày cụ thể (từ 2016-01-02)
# Columns: ['name', 'branch', 'buy_price', 'sell_price', 'date']

# === Giá vàng Bảo Tín Minh Châu ===
from vnstock.explorer.misc import btmc_goldprice
btmc = btmc_goldprice()
# Columns: ['name', 'karat', 'gold_content', 'buy_price', 'sell_price', 'world_price', 'time']

# === Tỷ giá VCB ===
from vnstock.explorer.misc import vcb_exchange_rate
fx = vcb_exchange_rate(date='2025-03-21')    # hoặc date='' cho ngày hiện tại
# Columns: ['currency_code', 'currency_name', 'buy_cash', 'buy_transfer', 'sell', 'date']

# === FX / Crypto / Chỉ số quốc tế (MSN) ===
from vnstock import Vnstock
fx_quote = Vnstock().fx(symbol='JPYVND', source='MSN')
fx_data = fx_quote.quote.history(start='2025-01-02', end='2025-03-20', interval='1D')
```

### 8. Chỉ Số & Hằng Số Thị Trường

```python
from vnstock.constants import INDICES_INFO, INDEX_GROUPS, SECTOR_IDS, EXCHANGES

# Thông tin chỉ số
# INDICES_INFO['VN30'] -> {'name': 'VN30', 'description': '...', 'group': 'HOSE Indices', ...}

# Nhóm chỉ số
# INDEX_GROUPS = {
#   'HOSE Indices': ['VN30', 'VNMID', 'VNSML', 'VN100', 'VNALL', 'VNSI'],
#   'Sector Indices': ['VNIT', 'VNIND', 'VNCONS', 'VNCOND', 'VNHEAL', 'VNENE', 'VNUTI', 'VNREAL', 'VNFIN', 'VNMAT'],
#   'Investment Indices': ['VNDIAMOND', 'VNFINLEAD', 'VNFINSELECT'],
#   'VNX Indices': ['VNX50', 'VNXALL'],
# }

# Phân loại ngành ICB
# SECTOR_IDS = {126: 'Dịch vụ viễn thông', 130: 'Hàng tiêu dùng', 138: 'Tài chính', ...}

# Sàn giao dịch
# EXCHANGES = {'HOSE': '...', 'HNX': '...', 'UPCOM': '...'}
```

### 9. CLI Helper - Truy vấn nhanh cực mạnh

Skill này cung cấp một CLI wrapper tích hợp sẵn cơ chế ưu tiên `KBS` và fallback `VCI` tự động:
- `python3 scripts/vnstock_cli.py price VCB --period 3M` (Lấy giá)
- `python3 scripts/vnstock_cli.py price VCB --intraday` (Giá nội ngày realtime)
- `python3 scripts/vnstock_cli.py finance VCB --report income --period quarter` (BCTC)
- `python3 scripts/vnstock_cli.py company VCB --info overview` (Thông tin DN)
- `python3 scripts/vnstock_cli.py listing --indices` (Danh sách chỉ số thị trường)
- `python3 scripts/vnstock_cli.py board VCB ACB` (Bảng giá nhanh)

---

## 🎯 Instructions - Quy Trình Xử Lý

### ⚡ ƯU TIÊN 1: Sử dụng CLI Script có sẵn (NHANH NHẤT)

**Skill này đã tích hợp sẵn CLI wrapper** tại `scripts/vnstock_cli.py` - đây là cách TRA CỨU NHANH nhất, không cần viết code.

#### Các lệnh CLI phổ biến:

```bash
# === GIÁ CỔ PHIẾU ===
python3 scripts/vnstock_cli.py price VCB --period 3M           # Giá 3 tháng
python3 scripts/vnstock_cli.py price VCB --period 1Y --tail 10 # 10 dòng cuối năm
python3 scripts/vnstock_cli.py price VCB --intraday            # Giá realtime nội ngày
python3 scripts/vnstock_cli.py price VCB --start 2024-01-01 --end 2024-12-31

# === BẢNG GIÁ REALTIME ===
python3 scripts/vnstock_cli.py board VCB ACB TCB BID CTG       # Nhiều mã cùng lúc

# === BÁO CÁO TÀI CHÍNH ===
python3 scripts/vnstock_cli.py finance VCB --report ratio      # Chỉ số tài chính (mặc định)
python3 scripts/vnstock_cli.py finance VCB --report income     # Kết quả kinh doanh
python3 scripts/vnstock_cli.py finance VCB --report balance --key-only  # Bảng cân đối (chỉ tiêu chính)
python3 scripts/vnstock_cli.py finance VCB --report cashflow   # Lưu chuyển tiền tệ

# === THÔNG TIN CÔNG TY ===
python3 scripts/vnstock_cli.py company VCB --info overview     # Thông tin tổng quan
python3 scripts/vnstock_cli.py company VCB --info shareholders # Cổ đông lớn
python3 scripts/vnstock_cli.py company VCB --info officers     # Ban lãnh đạo
python3 scripts/vnstock_cli.py company VCB --info news         # Tin tức
python3 scripts/vnstock_cli.py company VCB --info events       # Sự kiện

# === DANH SÁCH & CHỈ SỐ ===
python3 scripts/vnstock_cli.py listing --group VN30            # Mã trong VN30
python3 scripts/vnstock_cli.py listing --exchange HOSE         # Mã sàn HOSE
python3 scripts/vnstock_cli.py listing --industry Ngân hàng    # Mã ngành ngân hàng
python3 scripts/vnstock_cli.py listing --indices               # Tất cả chỉ số thị trường

# === TIỆN ÍKH ===
python3 scripts/vnstock_cli.py gold                            # Giá vàng SJC
python3 scripts/vnstock_cli.py fx --currency USD               # Tỷ giá USD
python3 scripts/vnstock_cli.py fund --type STOCK --top 10     # Top 10 quỹ cổ phiếu

# === ĐỊNH DẠNG ĐẦU RA ===
python3 scripts/vnstock_cli.py price VCB --format json > output.json   # JSON file
python3 scripts/vnstock_cli.py price VCB --format csv > output.csv     # CSV file
```

#### Ưu điểm của CLI Script:
- ✅ **Không cần viết code** - chạy là có kết quả ngay
- ✅ **Tự động fallback** KBS → VCI nếu nguồn chính không có dữ liệu
- ✅ **Hỗ trợ nhiều định dạng**: table (mặc định), JSON, CSV
- ✅ **Xử lý lỗi tự động** với thông báo rõ ràng
- ✅ **Tối ưu cho tra cứu nhanh** và scripting

#### Khi nào nên viết Python script thay vì dùng CLI:
- Cần phân tích phức tạp, tính toán tùy chỉnh
- Cần kết hợp nhiều API calls trong một logic
- Cần visualization hoặc export đặc biệt
- Cần batch processing số lượng lớn

---

### Bước 1: Phân tích yêu cầu người dùng

Khi người dùng hỏi về chứng khoán Việt Nam, xác định:
1. **Loại dữ liệu** cần lấy (giá, tài chính, thông tin công ty, bảng giá...)
2. **Mã chứng khoán** cụ thể (VCB, FPT, VNM...) hoặc nhóm (VN30, ngành ngân hàng...)
3. **Khoảng thời gian** nếu có
4. **Mức độ phân tích** (raw data vs đánh giá)

### Bước 2: Chọn phương pháp truy xuất

**Ưu tiên theo thứ tự:**
1. **CLI Script** (`scripts/vnstock_cli.py`) - cho tra cứu nhanh, dữ liệu tiêu chuẩn
2. **Python Script** - cho phân tích phức tạp, tính toán tùy chỉnh, kết hợp nhiều nguồn dữ liệu

### Bước 3: Chạy script

Chạy script Python qua terminal. Đảm bảo:
- Môi trường Python đã cài vnstock
- Kết nối internet ổn định
- Chạy trong giờ giao dịch (9:00-15:00 VN) nếu cần realtime

### Bước 4: Phân tích & trình bày kết quả

Sau khi có dữ liệu, agent nên:
- Tóm tắt và giải thích kết quả bằng ngôn ngữ người dùng đang sử dụng
- Highlight các chỉ số quan trọng
- Đưa ra nhận xét chung (KHÔNG đưa lời khuyên đầu tư)

---

## 📋 Các Tình Huống Phổ Biến

### Tình huống 1: Lấy giá cổ phiếu

**⚡ Cách nhanh nhất - Dùng CLI:**
```bash
python3 scripts/vnstock_cli.py price VCB --period 3M --tail 10
```

**Python script (cho phân tích tùy chỉnh):**
```python
from vnstock import Quote

quote = Quote(symbol='VCB', source='KBS')
df = quote.history(length='3M', interval='1D')
print(f"Giá 3 tháng gần nhất của VCB:")
print(df[['time', 'open', 'high', 'low', 'close', 'volume']].tail(10))
print(f"\nGiá đóng cửa gần nhất: {df['close'].iloc[-1]:,.0f} VND")
print(f"Thay đổi so với 1 tháng trước: {((df['close'].iloc[-1] / df['close'].iloc[-22]) - 1) * 100:.2f}%")
```

### Tình huống 2: Phân tích tài chính

**⚡ Cách nhanh nhất - Dùng CLI:**
```bash
python3 scripts/vnstock_cli.py finance VCB --report ratio --key-only
python3 scripts/vnstock_cli.py finance VCB --report income --key-only
```

**Python script (cho phân tích tùy chỉnh):**
```python
from vnstock import Finance

finance = Finance(symbol='VCB', source='KBS')

# Lấy chỉ số tài chính
ratios = finance.ratio(period='quarter')
key_ratios = ratios[ratios['item_id'].isin(['pe', 'pb', 'roe', 'roa', 'beta'])]
print("Chỉ số tài chính VCB:")
print(key_ratios[['item', 'item_id'] + [c for c in ratios.columns if 'Q' in c][:4]])

# Lấy doanh thu & lợi nhuận
income = finance.income_statement(period='quarter')
key_income = income[income['item_id'].isin(['revenue', 'net_profit'])]
print("\nDoanh thu & Lợi nhuận:")
print(key_income[['item', 'item_id'] + [c for c in income.columns if 'Q' in c][:4]])
```

### Tình huống 3: So sánh cổ phiếu

**Python script (cần tính toán tùy chỉnh):**
```python
from vnstock import Quote
import pandas as pd

symbols = ['VCB', 'ACB', 'TCB', 'BID', 'CTG']
results = []

for sym in symbols:
    try:
        quote = Quote(symbol=sym, source='KBS')
        df = quote.history(length='1Y', interval='1D')
        if df is not None and len(df) > 0:
            start_price = df['close'].iloc[0]
            end_price = df['close'].iloc[-1]
            ytd_return = ((end_price / start_price) - 1) * 100
            avg_volume = df['volume'].mean()
            results.append({
                'symbol': sym,
                'current_price': end_price,
                'ytd_return_%': round(ytd_return, 2),
                'avg_volume': int(avg_volume)
            })
    except Exception as e:
        print(f"Lỗi {sym}: {e}")

comparison = pd.DataFrame(results)
print("So sánh hiệu suất 1 năm:")
print(comparison.sort_values('ytd_return_%', ascending=False).to_string(index=False))
```

### Tình huống 4: Bảng giá realtime

**⚡ Cách nhanh nhất - Dùng CLI:**
```bash
python3 scripts/vnstock_cli.py board VCB ACB TCB BID CTG FPT VNM HPG MBB VPB
```

**Python script:**
```python
from vnstock import Trading

trading = Trading(source='KBS', symbol='VCB')
board = trading.price_board(symbols_list=['VCB', 'ACB', 'TCB', 'BID', 'CTG', 'FPT', 'VNM', 'HPG', 'MBB', 'VPB'])
print("Bảng giá realtime:")
print(board[['symbol', 'reference_price', 'close_price', 'price_change', 'percent_change', 'volume_accumulated']].to_string(index=False))
```

### Tình huống 5: Thông tin công ty

**⚡ Cách nhanh nhất - Dùng CLI:**
```bash
python3 scripts/vnstock_cli.py company FPT --info overview
python3 scripts/vnstock_cli.py company FPT --info shareholders
python3 scripts/vnstock_cli.py company FPT --info officers
```

**Python script:**
```python
from vnstock import Company

company = Company(source='KBS', symbol='FPT')
overview = company.overview()
print(f"Công ty: {overview['symbol'].iloc[0]}")
print(f"Sàn: {overview.get('exchange', ['N/A']).iloc[0] if 'exchange' in overview.columns else 'N/A'}")
print(f"Vốn điều lệ: {overview['charter_capital'].iloc[0]:,.0f} VND")

shareholders = company.shareholders()
print(f"\nCổ đông lớn:")
print(shareholders[['name', 'ownership_percentage']].to_string(index=False))

officers = company.officers()
print(f"\nBan lãnh đạo:")
print(officers[['name', 'position']].head(5).to_string(index=False))
```

### Tình huống 6: Giá vàng & tỷ giá

**⚡ Cách nhanh nhất - Dùng CLI:**
```bash
python3 scripts/vnstock_cli.py gold
python3 scripts/vnstock_cli.py fx --currency USD
```

**Python script:**
```python
from vnstock.explorer.misc import sjc_gold_price, vcb_exchange_rate

# Giá vàng hôm nay
gold = sjc_gold_price()
if gold is not None:
    print("Giá vàng SJC hôm nay:")
    print(gold[['name', 'buy_price', 'sell_price']].to_string(index=False))

# Tỷ giá USD hôm nay
from datetime import datetime
today = datetime.now().strftime('%Y-%m-%d')
fx = vcb_exchange_rate(date=today)
if fx is not None:
    usd = fx[fx['currency_code'] == 'USD']
    print(f"\nTỷ giá USD/VND (VCB):")
    print(usd[['currency_code', 'buy_cash', 'buy_transfer', 'sell']].to_string(index=False))
```

---

## ⚠️ Rules & Safety

### PHẢI làm:
1. **Luôn dùng try/except** khi gọi API để xử lý lỗi mạng, rate limit
2. **ƯU TIÊN NGUỒN KBS**: Đây là nguồn khuyến nghị chính. Chỉ dùng `VCI` làm fallback hoặc khi cần dữ liệu đặc thù.
3. **Sử dụng CLI Helper**: Tận dụng `scripts/vnstock_cli.py` vì nó đã cài sẵn logic fallback KBS -> VCI.
4. **Kiểm tra kết quả rỗng** trước khi xử lý (df is None or len(df) == 0)
5. **Giải thích kết quả** bằng ngôn ngữ dễ hiểu cho người dùng
6. **Ghi rõ đơn vị** tiền tệ (VND), phần trăm (%), khối lượng (shares)

### KHÔNG ĐƯỢC làm:
1. ❌ **KHÔNG đưa lời khuyên đầu tư** - vnstock chỉ là công cụ dữ liệu
2. ❌ **KHÔNG dùng source TCBS** - đã deprecated
3. ❌ **KHÔNG gọi API quá nhanh** - tuân thủ rate limit (20-60 req/phút tùy tier)
4. ❌ **KHÔNG sử dụng dữ liệu cho giao dịch thực** - chỉ cho nghiên cứu cá nhân
5. ❌ **KHÔNG lưu API key của người dùng** vào code

### Xử lý lỗi:
- **Network Error / Timeout**: Retry 1-2 lần, đợi 3-5 giây giữa các lần
- **Invalid Symbol**: Kiểm tra mã CK bằng `Listing.all_symbols()` trước
- **Empty DataFrame**: Thông báo không có dữ liệu, gợi ý thử source khác
- **Rate Limit (403)**: Đợi 30-60 giây rồi thử lại
- **Import Error**: Hướng dẫn cài đặt `pip install -U vnstock`

---

## 💡 Tips

1. **⚡ ƯU TIÊN CLI SCRIPT**: Luôn thử `scripts/vnstock_cli.py` trước cho tra cứu nhanh - không cần viết code, có sẵn fallback logic
2. **Batch operations**: Lấy dữ liệu 1 lần, tái sử dụng nhiều lần
3. **Giờ giao dịch VN**: 9:00-11:30 (sáng), 13:00-15:00 (chiều), UTC+7
4. **Dữ liệu intraday**: Có sẵn đến trước 7:00 sáng ngày kế tiếp
5. **Period format KBS**: '2025-Q3', '2025-Q2' (quý), '2025', '2024' (năm)
6. **to_df=False** trả về Pandas Series, dùng `.tolist()` nếu cần list Python
7. **Vnstock interface**: `stock = Vnstock().stock(symbol='VCB', source='KBS')` cho phân tích 1 mã xuyên suốt
8. **Network timeout**: API có thể chậm 5-15s, nên đặt timeout và retry hợp lý
9. **FX data**: Dùng `Vnstock().fx(symbol='USDJPY', source='MSN')` cho dữ liệu ngoại hối quốc tế
10. **Proxy support**: Finance/Quote hỗ trợ `proxy_mode='rotate'` cho cloud environments
11. **CLI output formats**: Dùng `--format json` hoặc `--format csv` để export dễ dàng
12. **CLI tail option**: Dùng `--tail 10` để chỉ xem N dòng cuối (tiện cho dữ liệu lớn)
