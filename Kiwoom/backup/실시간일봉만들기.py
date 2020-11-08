'''
장중일 때 테스트 구간 start
'''
# 분봉

# if "date_list" not in self.portfolio_stock_dict[sCode]:
#     self.portfolio_stock_dict[sCode].update({"date_list": []})
#
# if "date_list" in self.portfolio_stock_dict[sCode]:
#     temp_list = self.portfolio_stock_dict[sCode]["date_list"]
#     temp_list.append(a[:-2])
#
#     self.portfolio_stock_dict[sCode].update({"date_list": list(set(temp_list))})
#
# # print("self.portfolio_stock_dict date_list : {}".format(self.portfolio_stock_dict[sCode]["date_list"]))
#
# if "분봉" not in self.portfolio_stock_dict[sCode]:
#     self.portfolio_stock_dict[sCode].update({"분봉": {}})
#
# if "분봉" in self.portfolio_stock_dict[sCode]:
#     for minute in self.portfolio_stock_dict[sCode]["date_list"]:
#         # print("minute : {}".format(minute))
#         if minute not in self.portfolio_stock_dict[sCode]["분봉"]:
#             self.portfolio_stock_dict[sCode]["분봉"].update({minute: {}})
#
# if a[:-2] in self.portfolio_stock_dict[sCode]["분봉"]:
#     volume = 0
#     if "volume" not in self.portfolio_stock_dict[sCode]["분봉"][a[:-2]]:
#         self.portfolio_stock_dict[sCode]["분봉"][a[:-2]].update({"volume": 0})
#
#     if "volume" in self.portfolio_stock_dict[sCode]["분봉"][a[:-2]]:
#         volume = self.portfolio_stock_dict[sCode]["분봉"][a[:-2]]["volume"] + abs(g)
#         self.portfolio_stock_dict[sCode]["분봉"][a[:-2]].update({"volume": volume})
#
#     if "close" not in self.portfolio_stock_dict[sCode]["분봉"][a[:-2]]:
#         self.portfolio_stock_dict[sCode]["분봉"][a[:-2]].update({"close": 0})
#
#     if "close" in self.portfolio_stock_dict[sCode]["분봉"][a[:-2]]:
#         self.portfolio_stock_dict[sCode]["분봉"][a[:-2]].update({"close": b})

# # 초봉
# if "sec_list" not in self.account_stock_dict[sCode]:
#     self.account_stock_dict[sCode].update({"sec_list": []})
#
# if "sec_list" in self.account_stock_dict[sCode]:
#     temp_list = self.account_stock_dict[sCode]["sec_list"]
#     temp_list.append(a)
#
#     self.account_stock_dict[sCode].update({"sec_list": list(set(temp_list))})
#
# if "초봉" not in self.account_stock_dict[sCode]:
#     self.account_stock_dict[sCode].update({"초봉": {}})
#
# if "초봉" in self.account_stock_dict[sCode]:
#     for sec in self.account_stock_dict[sCode]["sec_list"]:
#         # print("minute : {}".format(minute))
#         if sec not in self.account_stock_dict[sCode]["초봉"]:
#             self.account_stock_dict[sCode]["초봉"].update({sec: {}})
#
# if a in self.account_stock_dict[sCode]["초봉"]:
#     volume = 0
#     if "volume" not in self.account_stock_dict[sCode]["초봉"][a]:
#         self.account_stock_dict[sCode]["초봉"][a].update({"volume": 0})
#
#     if "volume" in self.account_stock_dict[sCode]["초봉"][a]:
#         volume = self.account_stock_dict[sCode]["초봉"][a]["volume"] + abs(g)
#         self.account_stock_dict[sCode]["초봉"][a].update({"volume": volume})
#
#     if "close" not in self.account_stock_dict[sCode]["초봉"][a]:
#         self.account_stock_dict[sCode]["초봉"][a].update({"close": 0})
#
#     if "close" in self.account_stock_dict[sCode]["초봉"][a]:
#         self.account_stock_dict[sCode]["초봉"][a].update({"close": b})

# print("self.portfolio_stock_dict : {}".format(self.portfolio_stock_dict[sCode]["분봉"]))

# df = pd.DataFrame(self.portfolio_stock_dict[sCode]["분봉"])
# df = df.T

# df_sec = pd.DataFrame(self.account_stock_dict[sCode]["초봉"])
# df_sec = df_sec.T
#
# df_sec['ma20'] = df_sec['close'].rolling(window=20).mean()
# df_sec['ma20_dpc'] = (df_sec['ma20'] / df_sec['ma20'].shift(1) - 1) * 100
# df_sec['ma3v'] = df_sec['volume'].rolling(window=3).mean()
# df_sec['ma3v_dpc'] = (df_sec['ma3v'] / df_sec['ma3v'].shift(1) - 1) * 100
#
# if len(df) > 3 and len(df) < 7:
#     if df['open'][-3] > df['close'][-3] and df['open'][-2] > df['close'][-2]:  # 2연속 음봉
#
#         if df['open'][-1] > df['close'][-1]: # 현재 분봉이 양봉이 되면 sql 호출 안하게
#             seq = self.mk.get_buy_stock_info_max_seq(sCode, self.datetime)
#
#             buy_stock = self.mk.get_buy_stock_info(sCode, self.datetime, seq, '매수')
#
#             # print("seq : {}".format(seq))
#             # print("df : {}".format(df))
#             if len(buy_stock) > 0:
#                 with self.mk.conn.cursor() as curs:
#                     sql = "UPDATE buy_stock_info SET real_event_msg = {} where code = {} and buy_date = '{}' and seq = '{}' ".format('분봉확인바람', sCode, self.datetime, seq)
#                     curs.execute(sql)
#                     self.mk.conn.commit()
#                 self.slack.chat.post_message("hellojarvis", "코드 : " + sCode + " 2연속 음봉, 분봉확인 요청")
#
# if len(df) >= 7:
#
#     df['ma5'] = df['close'].rolling(window=5).mean()
#     df['ma5_dpc'] = (df['ma5'] / df['ma5'].shift(1) - 1) * 100
#     if df['ma5_dpc'][-4:].max() < 0:
#         if df['open'][-1] > df['close'][-1]: # 현재 분봉이 양봉이 되면 sql 호출 안하게
#             seq = self.mk.get_buy_stock_info_max_seq(sCode, self.datetime)
#
#             buy_stock = self.mk.get_buy_stock_info(sCode, self.datetime, seq, '매수')
#
#             if len(buy_stock) > 0:
#                 with self.mk.conn.cursor() as curs:
#                     sql = "UPDATE buy_stock_info SET real_event_msg = {} where code = {} and buy_date = '{}' and seq = '{}' ".format('분봉확인바람', sCode, self.datetime, seq)
#                     curs.execute(sql)
#                     self.mk.conn.commit()
#                 self.slack.chat.post_message("hellojarvis", "코드 : " + sCode + " 5일 이평선 4분 연속 하락, 분봉확인 요청")

# df['ma10'] = df['close'].rolling(window=10).mean()
# df['ma20'] = df['close'].rolling(window=20).mean()
# df['ma20_dpc'] = (df['ma20'] / df['ma20'].shift(1) - 1) * 100
# df['ma3v'] = df['volume'].rolling(window=3).mean()
# df['ma3v_dpc'] = (df['ma3v'] / df['ma3v'].shift(1) - 1) * 100
# # if 8% 먹으면 매도:
# # elif 8% 이하:
#
# if df['ma20_dpc'][-2] > 0:  # 20일선 상승하다가
#     if df['open'][-4] > df['close'][-4] and df['open'][-3] > df['close'][-3] and df['open'][-2] > \
#             df['close'][-2]:  # 3분 연속 음봉봉
#         if df['ma3v_dpc'][-2] > 0:  # 거래량까지 실리면
#             if df['ma20'][-2] > df['close'][-2]:
#                 if "for_msg_num" not in self.account_stock_dict[sCode]:
#                     self.account_stock_dict[sCode].update({"for_msg_num": len(df)})
#
#                 if self.account_stock_dict[sCode]['for_msg_num'] == len(df):
#                     msg = sCode + " 매도 타이밍인지 확인"
#                     self.slack.chat.post_message("hellojarvis", msg)
#                     self.account_stock_dict[sCode].update({"for_msg_num": -1})
'''
장중일 때 테스트 구간 end
'''

# print("self.portfolio_stock_dict : {}".format(self.portfolio_stock_dict))
