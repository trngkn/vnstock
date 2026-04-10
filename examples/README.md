# Vnstock OpenClaw Skill - Examples

## Quick Reference Examples

### 1. Giá cổ phiếu

```python
# Lấy giá 3 tháng gần nhất
from vnstock import Quote
quote = Quote(symbol='FPT', source='KBS')
df = quote.history(length='3M', interval='1D')
print(df[['time', 'close', 'volume']].tail(5))
```

### 2. Chỉ số tài chính nhanh

```python
from vnstock import Finance
finance = Finance(symbol='FPT', source='KBS')
ratios = finance.ratio(period='quarter')
for _, row in ratios.iterrows():
    if row['item_id'] in ['pe', 'pb', 'roe', 'roa']:
        periods = [c for c in ratios.columns if 'Q' in c][:1]
        val = row[periods[0]] if periods else 'N/A'
        print(f"  {row['item']}: {val}")
```

### 3. Top 5 cổ phiếu ngân hàng theo hiệu suất

```python
from vnstock import Listing, Quote
import pandas as pd

listing = Listing(source='KBS')
banks = listing.symbols_by_industries(industry_name='Ngân hàng', to_df=True)
bank_symbols = banks['symbol'].tolist()[:10]  # Lấy 10 mã đầu

results = []
for sym in bank_symbols:
    try:
        quote = Quote(symbol=sym, source='KBS')
        df = quote.history(length='1Y', interval='1D')
        if df is not None and len(df) > 20:
            ret = ((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100
            results.append({'symbol': sym, 'return_1y': round(ret, 2)})
    except:
        pass

result_df = pd.DataFrame(results).sort_values('return_1y', ascending=False)
print("Top ngân hàng theo hiệu suất 1 năm:")
print(result_df.head(5).to_string(index=False))
```

### 4. Danh mục VN30

```python
from vnstock import Listing
listing = Listing(source='KBS')
vn30 = listing.symbols_by_group(group_name='VN30', to_df=False).tolist()
print(f"VN30 ({len(vn30)} mã): {', '.join(vn30)}")
```

### 5. Giá nội ngày (Intraday)

```python
from vnstock import Quote
quote = Quote(symbol='FPT', source='KBS')
intraday = quote.intraday(page_size=50)
print("Dữ liệu khớp lệnh 50 phiên gần nhất:")
print(intraday[['time', 'price', 'volume', 'match_type']].head())
```

### 6. CLI Usage

Skill hỗ trợ một CLI wrapper mạnh mẽ (`scripts/vnstock_cli.py`) với cơ chế **tự động fallback** từ KBS sang VCI nếu dữ liệu trống.

```bash
# 1. Giá cổ phiếu (Mặc định 3 tháng gần nhất)
python scripts/vnstock_cli.py price VCB --period 1Y --tail 10
# Lấy giá nội ngày (ticks)
python scripts/vnstock_cli.py price VCB --intraday --page-size 50

# 2. Bảng giá realtime (Nhiều mã)
python scripts/vnstock_cli.py board VCB ACB TCB FPT VNM

# 3. Báo cáo tài chính
# Mặc định lấy chỉ số tài chính (ratio), hỗ trợ display-mode cho vnstock 3.4+
python scripts/vnstock_cli.py finance VCB --report income --display-mode all
# Chỉ lấy các chỉ tiêu chính (KBS level 1)
python scripts/vnstock_cli.py finance VCB --report balance --key-only

# 4. Thông tin công ty & Niêm yết
python scripts/vnstock_cli.py company VCB --info overview
python scripts/vnstock_cli.py company VCB --info affiliate  # Công ty liên kết
python scripts/vnstock_cli.py listing --indices             # Các chỉ số thị trường

# 5. Tiện ích: Vàng, Tỷ giá, Quỹ mở
python scripts/vnstock_cli.py gold
python scripts/vnstock_cli.py fx --currency USD
python scripts/vnstock_cli.py fund --type STOCK --top 5

# 6. Định dạng đầu ra (Table, JSON, CSV)
python scripts/vnstock_cli.py price VCB --format json > vcb_price.json
```
