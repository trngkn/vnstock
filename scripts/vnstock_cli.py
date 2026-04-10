#!/usr/bin/env python3
"""
vnstock CLI wrapper - OpenClaw Skill Helper
Provides quick access to vnstock data via command line.

Usage:
  python vnstock_cli.py price VCB --period 3M
  python vnstock_cli.py finance VCB --report income --period quarter
  python vnstock_cli.py company VCB --info overview
  python vnstock_cli.py listing --group VN30
  python vnstock_cli.py board VCB ACB TCB
  python vnstock_cli.py gold
  python vnstock_cli.py fx --date 2025-03-21
  python vnstock_cli.py fund --type STOCK --top 10
"""

import sys
import argparse
import json
from datetime import datetime


def cmd_price(args):
    """Lấy giá cổ phiếu lịch sử hoặc intraday."""
    from vnstock import Quote
    
    def fetch_data(source):
        quote = Quote(symbol=args.symbol, source=source)
        if args.intraday:
            return quote.intraday(page_size=args.page_size)
        if args.start:
            return quote.history(start=args.start, end=args.end or datetime.now().strftime('%Y-%m-%d'), interval=args.interval)
        return quote.history(length=args.period, interval=args.interval)

    df = fetch_data(args.source)
    
    # Fallback to VCI if KBS fails and user didn't explicitly request VCI
    if (df is None or len(df) == 0) and args.source == 'KBS':
        print(f"⚠️ KBS không có dữ liệu cho {args.symbol}, đang thử lại với VCI...")
        df = fetch_data('VCI')

    if df is None or len(df) == 0:
        print(f"❌ Không có dữ liệu cho {args.symbol}")
        return
    
    if args.format == 'json':
        print(df.to_json(orient='records', date_format='iso', force_ascii=False))
    elif args.format == 'csv':
        print(df.to_csv(index=False))
    else:
        label = "Giá nội ngày" if args.intraday else f"Giá lịch sử ({args.period or f'{args.start} → {args.end}'})"
        print(f"\n📊 {label} {args.symbol}:")
        print(f"{'─' * 80}")
        
        # Determine columns to show
        if args.intraday:
            cols = ['time', 'price', 'volume', 'match_type']
        else:
            cols = ['time', 'open', 'high', 'low', 'close', 'volume']
        
        cols = [c for c in cols if c in df.columns]
        
        if args.tail:
            print(df[cols].tail(args.tail).to_string(index=False))
        else:
            print(df[cols].to_string(index=False))
        
        if not args.intraday:
            # Summary stats
            print(f"\n📈 Tóm tắt:")
            if 'close' in df.columns:
                print(f"  Giá đóng cửa gần nhất: {df['close'].iloc[-1]:,.0f}")
                if len(df) > 1:
                    change = ((df['close'].iloc[-1] / df['close'].iloc[0]) - 1) * 100
                    print(f"  Thay đổi kỳ: {change:+.2f}%")
            if 'high' in df.columns: print(f"  Giá cao nhất: {df['high'].max():,.0f}")
            if 'low' in df.columns: print(f"  Giá thấp nhất: {df['low'].min():,.0f}")
            if 'volume' in df.columns: print(f"  KL trung bình: {df['volume'].mean():,.0f}")


def cmd_finance(args):
    """Lấy báo cáo tài chính."""
    from vnstock import Finance
    
    def fetch_data(source):
        finance = Finance(symbol=args.symbol, source=source)
        report_map = {
            'income': finance.income_statement,
            'balance': finance.balance_sheet,
            'cashflow': finance.cash_flow,
            'ratio': finance.ratio,
        }
        func = report_map.get(args.report)
        if not func: return None
        
        # Support display_mode for version 3.4.0+
        try:
            return func(period=args.period, display_mode=args.display_mode)
        except TypeError:
            # Fallback if display_mode is not supported by the function/version
            return func(period=args.period)

    df = fetch_data(args.source)
    
    # Fallback to VCI
    if (df is None or len(df) == 0) and args.source == 'KBS':
        print(f"⚠️ KBS không có dữ liệu tài chính cho {args.symbol}, đang thử lại với VCI...")
        df = fetch_data('VCI')
    
    if df is None or len(df) == 0:
        print(f"❌ Không có dữ liệu tài chính cho {args.symbol}")
        return
    
    if args.format == 'json':
        print(df.to_json(orient='records', force_ascii=False))
    elif args.format == 'csv':
        print(df.to_csv(index=False))
    else:
        report_names = {
            'income': 'Kết quả kinh doanh',
            'balance': 'Bảng cân đối kế toán',
            'cashflow': 'Lưu chuyển tiền tệ',
            'ratio': 'Chỉ số tài chính',
        }
        print(f"\n💰 {report_names[args.report]} - {args.symbol} ({args.period}, mode: {args.display_mode}):")
        print(f"{'─' * 80}")
        
        if args.key_only and 'levels' in df.columns:
            df = df[df['levels'] == 1]
        
        # Show main columns
        # Period columns usually contain Q or are years
        period_cols = [c for c in df.columns if 'Q' in str(c) or str(c).isdigit()][:4]
        show_cols = ['item', 'item_id'] + period_cols
        # If VCI, it uses different names like ticker, yearReport, etc.
        if 'ticker' in df.columns:
             show_cols = [c for c in df.columns if c not in ['ticker']]
             
        show_cols = [c for c in show_cols if c in df.columns]
        print(df[show_cols].to_string(index=False))


def cmd_company(args):
    """Lấy thông tin công ty."""
    from vnstock import Company
    
    def fetch_data(source):
        company = Company(source=source, symbol=args.symbol)
        info_map = {
            'overview': company.overview,
            'shareholders': company.shareholders,
            'officers': company.officers,
            'news': company.news,
            'events': company.events,
            'subsidiaries': company.subsidiaries,
            'affiliate': company.affiliate,
        }
        func = info_map.get(args.info)
        if not func: return None
        return func()

    df = fetch_data(args.source)
    
    # Fallback to VCI
    if (df is None or len(df) == 0) and args.source == 'KBS':
        print(f"⚠️ KBS không có dữ liệu {args.info} cho {args.symbol}, đang thử lại với VCI...")
        df = fetch_data('VCI')
        
    if df is None or len(df) == 0:
        print(f"⚠️ Không có dữ liệu {args.info} cho {args.symbol}")
        return
    
    if args.format == 'json':
        print(df.to_json(orient='records', force_ascii=False))
    elif args.format == 'csv':
        print(df.to_csv(index=False))
    else:
        info_names = {
            'overview': 'Thông tin tổng quan',
            'shareholders': 'Cổ đông lớn',
            'officers': 'Ban lãnh đạo',
            'news': 'Tin tức',
            'events': 'Sự kiện',
            'subsidiaries': 'Công ty con',
            'affiliate': 'Công ty liên kết',
        }
        print(f"\n🏢 {info_names[args.info]} - {args.symbol}:")
        print(f"{'─' * 80}")
        print(df.to_string(index=False))


def cmd_listing(args):
    """Lấy danh sách chứng khoán."""
    from vnstock import Listing
    
    def fetch_data(source):
        listing = Listing(source=source)
        if args.group:
            return listing.symbols_by_group(group_name=args.group, to_df=True)
        elif args.exchange:
            return listing.symbols_by_exchange(exchange=args.exchange, to_df=True)
        elif args.industry:
            return listing.symbols_by_industries(industry_name=args.industry, to_df=True)
        elif args.indices:
            if args.indices_group:
                return listing.indices_by_group(group_name=args.indices_group)
            return listing.all_indices()
        else:
            return listing.all_symbols(to_df=True)

    df = fetch_data(args.source)
    
    # Fallback to VCI
    if (df is None or len(df) == 0) and args.source == 'KBS':
        # Don't print warning for listing as it might be common if group is empty in KBS
        df = fetch_data('VCI')
    
    if df is None or len(df) == 0:
        print(f"❌ Không tìm thấy mã CK")
        return
    
    if args.format == 'json':
        print(df.to_json(orient='records', force_ascii=False))
    elif args.format == 'csv':
        print(df.to_csv(index=False))
    else:
        label = "Danh sách mã CK"
        if args.group: label = f"Nhóm {args.group}"
        if args.exchange: label = f"Sàn {args.exchange}"
        if args.industry: label = f"Ngành {args.industry}"
        if args.indices: label = "Danh sách chỉ số"
        
        print(f"\n📋 {label}: {len(df)} bản ghi")
        print(f"{'─' * 60}")
        print(df.to_string(index=False))


def cmd_board(args):
    """Lấy bảng giá realtime."""
    from vnstock import Trading
    
    def fetch_data(source):
        trading = Trading(source=source, symbol=args.symbols[0])
        return trading.price_board(symbols_list=args.symbols)

    board = fetch_data(args.source)
    
    # Fallback to VCI
    if (board is None or len(board) == 0) and args.source == 'KBS':
        board = fetch_data('VCI')
    
    if board is None or len(board) == 0:
        print("❌ Không có dữ liệu bảng giá")
        return
    
    if args.format == 'json':
        print(board.to_json(orient='records', force_ascii=False))
    elif args.format == 'csv':
        print(board.to_csv(index=False))
    else:
        print(f"\n📊 Bảng giá realtime (source: {args.source}):")
        print(f"{'─' * 80}")
        cols = ['symbol', 'reference_price', 'close_price', 'price_change', 'percent_change', 'volume_accumulated']
        show_cols = [c for c in cols if c in board.columns]
        print(board[show_cols].to_string(index=False))


def cmd_gold(args):
    """Lấy giá vàng."""
    from vnstock.explorer.misc import sjc_gold_price
    
    gold = sjc_gold_price(date=args.date)
    
    if gold is None or len(gold) == 0:
        print("❌ Không có dữ liệu giá vàng")
        return
    
    if args.format == 'json':
        print(gold.to_json(orient='records', force_ascii=False))
    else:
        print(f"\n🥇 Giá vàng SJC ({args.date or 'Hôm nay'}):")
        print(f"{'─' * 60}")
        print(gold[['name', 'branch', 'buy_price', 'sell_price']].to_string(index=False))


def cmd_fx(args):
    """Lấy tỷ giá ngoại tệ."""
    from vnstock.explorer.misc import vcb_exchange_rate
    
    date = args.date or datetime.now().strftime('%Y-%m-%d')
    fx = vcb_exchange_rate(date=date)
    
    if fx is None or len(fx) == 0:
        print("❌ Không có dữ liệu tỷ giá")
        return
    
    if args.format == 'json':
        print(fx.to_json(orient='records', force_ascii=False))
    else:
        print(f"\n💱 Tỷ giá VCB ({date}):")
        print(f"{'─' * 60}")
        if args.currency:
            fx = fx[fx['currency_code'] == args.currency.upper()]
        print(fx[['currency_code', 'currency_name', 'buy_cash', 'buy_transfer', 'sell']].to_string(index=False))


def cmd_fund(args):
    """Lấy thông tin quỹ đầu tư."""
    from vnstock import Fund
    
    fund = Fund()
    funds = fund.listing(fund_type=args.type or '')
    
    if funds is None or len(funds) == 0:
        print("❌ Không có dữ liệu quỹ đầu tư")
        return
    
    # Sort by 1Y return
    funds = funds.sort_values('nav_change_12m', ascending=False)
    
    if args.top:
        funds = funds.head(args.top)
    
    if args.format == 'json':
        print(funds.to_json(orient='records', force_ascii=False))
    else:
        print(f"\n📊 Quỹ đầu tư mở ({args.type or 'Tất cả'}):")
        print(f"{'─' * 80}")
        cols = ['short_name', 'name', 'fund_type', 'nav', 'nav_change_12m', 'management_fee']
        show_cols = [c for c in cols if c in funds.columns]
        print(funds[show_cols].to_string(index=False))


def main():
    parser = argparse.ArgumentParser(description='vnstock CLI - Dữ liệu chứng khoán VN')
    parser.add_argument('--source', default='KBS', help='Nguồn dữ liệu (KBS/VCI)')
    parser.add_argument('--format', choices=['table', 'json', 'csv'], default='table', help='Định dạng output')
    
    subparsers = parser.add_subparsers(dest='command', help='Lệnh')
    
    # Price
    p_price = subparsers.add_parser('price', help='Giá cổ phiếu lịch sử hoặc nội ngày')
    p_price.add_argument('symbol', help='Mã CK (VD: VCB)')
    p_price.add_argument('--period', default='3M', help='Khoảng thời gian (1M/3M/6M/1Y/2Y/100b)')
    p_price.add_argument('--start', help='Ngày bắt đầu (YYYY-MM-DD)')
    p_price.add_argument('--end', help='Ngày kết thúc (YYYY-MM-DD)')
    p_price.add_argument('--interval', default='1D', help='Interval (1m/5m/15m/30m/1H/1D/1W/1M)')
    p_price.add_argument('--intraday', action='store_true', help='Lấy giá nội ngày (realtime ticks)')
    p_price.add_argument('--page-size', type=int, default=100, help='Số lượng bản ghi intraday')
    p_price.add_argument('--tail', type=int, help='Chỉ hiển thị N dòng cuối')
    
    # Finance
    p_fin = subparsers.add_parser('finance', help='Báo cáo tài chính')
    p_fin.add_argument('symbol', help='Mã CK')
    p_fin.add_argument('--report', default='ratio', choices=['income', 'balance', 'cashflow', 'ratio'])
    p_fin.add_argument('--period', default='quarter', choices=['quarter', 'year'])
    p_fin.add_argument('--display-mode', default='std', choices=['std', 'all', 'auto', 'vi', 'en'], help='Chế độ hiển thị trường dữ liệu (v3.4+)')
    p_fin.add_argument('--key-only', action='store_true', help='Chỉ hiển thị chỉ tiêu chính (KBS level 1)')
    
    # Company
    p_comp = subparsers.add_parser('company', help='Thông tin công ty')
    p_comp.add_argument('symbol', help='Mã CK')
    p_comp.add_argument('--info', default='overview', 
                        choices=['overview', 'shareholders', 'officers', 'news', 'events', 'subsidiaries', 'affiliate'])
    
    # Listing
    p_list = subparsers.add_parser('listing', help='Danh sách mã CK & Chỉ số')
    p_list.add_argument('--group', help='Nhóm chỉ số (VN30/VN100/...)')
    p_list.add_argument('--exchange', help='Sàn (HOSE/HNX/UPCOM)')
    p_list.add_argument('--industry', help='Ngành')
    p_list.add_argument('--indices', action='store_true', help='Liệt kê các chỉ số thị trường')
    p_list.add_argument('--indices-group', help='Lọc chỉ số theo nhóm (HOSE Indices/Sector Indices/...)')
    
    # Board
    p_board = subparsers.add_parser('board', help='Bảng giá realtime')
    p_board.add_argument('symbols', nargs='+', help='Danh sách mã CK')
    
    # Gold
    p_gold = subparsers.add_parser('gold', help='Giá vàng SJC')
    p_gold.add_argument('--date', help='Ngày (YYYY-MM-DD)')
    
    # FX
    p_fx = subparsers.add_parser('fx', help='Tỷ giá ngoại tệ VCB')
    p_fx.add_argument('--date', help='Ngày (YYYY-MM-DD)')
    p_fx.add_argument('--currency', help='Mã ngoại tệ (USD/EUR/JPY...)')
    
    # Fund
    p_fund = subparsers.add_parser('fund', help='Quỹ đầu tư mở')
    p_fund.add_argument('--type', choices=['STOCK', 'BOND', 'BALANCED'], help='Loại quỹ')
    p_fund.add_argument('--top', type=int, help='Top N quỹ theo lợi suất')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    commands = {
        'price': cmd_price,
        'finance': cmd_finance,
        'company': cmd_company,
        'listing': cmd_listing,
        'board': cmd_board,
        'gold': cmd_gold,
        'fx': cmd_fx,
        'fund': cmd_fund,
    }
    
    try:
        commands[args.command](args)
    except ImportError as e:
        print(f"❌ vnstock chưa được cài đặt: {e}")
        print(f"  Chạy: pip install -U vnstock")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
