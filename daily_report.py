# -*- coding:UTF-8 -*-
from datetime import datetime
from redminelib import Redmine
import pymysql
import matplotlib.pyplot as plt
import configparser

config = configparser.ConfigParser()
config.read("./properties.init")
config_mysql=config['Mysql']
config_Redmine=config['Redmine']
config_Plan=config['Plan']

# 缺陷对应人员的数量及缺陷模块数量
def current_day():
    resolve_user_list,module_list,all_user_list = [],[],[]
    # test_rate edition
    i = 0
    with open('curren.txt', 'r', encoding='UTF-8') as file_current_read:
        current_lines = file_current_read.readlines()
        for line in current_lines:
            i += 1
            if i == 2: install_time = line
            if i == 4: branch = line
            if i == 6: git_log = line
    test_edition=[install_time,branch,git_log]
    # user
    with open('user.txt', 'r',encoding='UTF-8') as file_user_read:
        user_lines = file_user_read.readlines()
        for user in user_lines:
            n = 0
            j = 0
            for issue in issues_open:
                if issue.assigned_to.name + '\n' == user:
                    j +=1
                    if issue.status.name == "已解决":
                        n += 1
            resolve_user_list.append([user[:-1],n]) #已解决的人员分布
            all_user_list.append([user[:-1],j])
        # module
        with open('module.txt', 'r', encoding='UTF-8') as file_module_read:
            module_lines = file_module_read.readlines()
            for module in module_lines:
                n = 0
                for issue in issues_open:
                    if issue.custom_fields._resources[2]['value'] + '\n' == module:
                        n += 1
                module_list.append([module[:-1],n])
    return resolve_user_list,module_list,all_user_list,test_edition
    # current_day[0] 已解决人员对应# current_day[1] 模块对应# current_day[2] 人员对应 #current_day[3]版本信息


def test_rate():
    tester_list=config_Plan['tester'].split(',')
    every_tester_list = []
    for tester in tester_list:
        user_newnum,results_all,results_execute = 0,0,0
        deadly_list, stop_list = '', ''
        test_module= []
        # -计算testlink进度--
        testlink_db = pymysql.connect(host=config_mysql['testlink_host'], port=int(config_mysql['port']),user=config_mysql['testlink_user'], passwd=config_mysql['testlink_passwd'],db='testlink')
        cursor = testlink_db.cursor()
        try:
            name_sql=tester.split(' ')
            sql_all = "select COUNT(*) from user_assignments WHERE build_id=(SELECT id FROM builds WHERE name='%s') and user_id=(SELECT id from users where last='%s' and first='%s')" % (config_Plan['test_version'],name_sql[0],name_sql[1])
            cursor.execute(sql_all)  # 执行SQL语句
            results_all = cursor.fetchall()  # 获取所有记录列表
            sql_execute = "select COUNT(*) from executions WHERE build_id=(SELECT id FROM builds WHERE name='%s') and tester_id=(SELECT id from users where last='%s' and first='%s')" % (config_Plan['test_version'],name_sql[0],name_sql[1])
            cursor.execute(sql_execute)  # 执行SQL语句
            results_execute = cursor.fetchall()  # 获取所有记录列表
            print('ok')
        except:
            print("Error: unable to fetch data")
        testlink_db.close()
        tester_rate = round(results_execute[0][0]*100/results_all[0][0],2)
        # ----
        for issue in issues_all:
            create_time = str(issue.created_on.year) + "-" + str(issue.created_on.month) + "-" + str(issue.created_on.day)
            if create_time == today and issue.author.name == tester:
                    user_newnum += 1    #测试每日创建的缺陷数
                    if not issue.custom_fields._resources[2]['value'] in test_module:
                        test_module.append(issue.custom_fields._resources[2]['value'])
                    if issue.custom_fields._resources[0]['value'] == "重大" or issue.custom_fields._resources[0]['value'] == "致命":
                        deadly_list = deadly_list + str(issue.subject + ' ')  # --严重缺陷描述
                    if issue.custom_fields._resources[0]['value'] == "重大" and issue.priority['name'] == "紧急":
                        stop_list = stop_list + str(issue.subject + ' ')  # -- 阻塞缺陷描述
        every_tester_list.append([tester,str(test_module)[1:-1],'1.测试进度:'+str(tester_rate)+'%','2.提交bug数:'+str(user_newnum)+'个','3.提交的严重问题:'+deadly_list,'4.阻塞进度的问题描述:'+stop_list])
    return every_tester_list


def analysis():
    # 严重 grave 致命 deadly 紧急 urgent 已解决 resolved  超时 timeout 阻塞 stop
    become_list,grave_list,stop_list = [],[],[]  #退化缺陷 、重大、阻塞
    become_re, grave_re, stop_re = [], [], []  # 退化缺陷已解决 、重大已解决、阻塞已解决
    become,grave_num, deadly_num, timeout_num,stop_num,resolved_all = 0, 0, 0, 0, 0, 0
    for issue in issues_open:
        update_time = str(issue.updated_on.year) + "-" + str(issue.updated_on.month) + "-" + str(issue.updated_on.day)
        updatetime_date = datetime.strptime(update_time, '%Y-%m-%d')
        today_date = datetime.strptime(today, '%Y-%m-%d')
        delta = today_date - updatetime_date
        if delta.days >= 7: timeout_num += 1
        if issue.custom_fields._resources[0]['value'] == "重大" or issue.custom_fields._resources[0]['value'] == "致命": deadly_num += 1
        if issue.custom_fields._resources[3]['value'] == '1':
            become += 1
            if issue.status.name == "已解决":
                become_re.append([issue.assigned_to.name, issue.status.name, issue.id, issue.subject])
            else:
                become_list.append([issue.assigned_to.name, issue.status.name, issue.id, issue.subject])
        if issue.custom_fields._resources[0]['value'] == "重大" and issue.priority['name'] == "紧急":
            stop_num += 1
            if issue.status.name == "已解决":
                stop_re.append([issue.assigned_to.name, issue.status.name, issue.id, issue.subject])
            else:
                stop_list.append([issue.assigned_to.name, issue.status.name, issue.id, issue.subject])
        if issue.status.name == "已解决": resolved_all += 1
        if issue.custom_fields._resources[0]['value'] == "重大":
            grave_num += 1
            if issue.status.name == "已解决":
                grave_re.append([issue.assigned_to.name, issue.status.name, issue.id, issue.subject])
            else:
                grave_list.append([issue.assigned_to.name, issue.status.name, issue.id, issue.subject])
    analysis_list=[grave_list+grave_re,stop_list+stop_re,grave_num,deadly_num,resolved_all,timeout_num,become,become_list+become_re]
    return analysis_list
    #重大缺陷列表 [0]#阻塞缺陷列表 [1]#重大缺陷个数 [2] #重大/致命缺陷个数 [3]#已解决数 [4]# 超过一周未更新数 [5]#今日新增数 [6] # 退化数 [7] # 退化列表 [8]


def SandP_mysql():  # 
    x, new_num = 0, 0
    summer = [['时间', '已解决', '今日新建', '待解决问题']]
    daily_row = [['时间', '新建', '进行中', '已解决', '反馈', '阻塞', '推迟', 'Reopen']]
    new_all, ongoing_all, feedback_all, delay_all, reopen_all, block_all, resolved_all = 0, 0, 0, 0, 0, 0, 0
    for issue in issues_all:
        if issue.status.name == "新建": new_all += 1
        if issue.status.name == "进行中": ongoing_all += 1
        if issue.status.name == "已解决": resolved_all += 1
        if issue.status.name == "反馈": feedback_all += 1
        if issue.status.name == "推迟": delay_all += 1
        if issue.status.name == "重新打开": reopen_all += 1
        if issue.status.name == "阻塞": block_all += 1
        create_time = str(issue.created_on.year) + "-" + str(issue.created_on.month) + "-" + str(issue.created_on.day)
        if create_time == today:
            new_num += 1
    totle_unresolved = new_all + ongoing_all + feedback_all + delay_all + reopen_all + block_all  # 未解决
    daily_row.append([today, new_all, ongoing_all, resolved_all, feedback_all,block_all, delay_all,reopen_all])
    db = pymysql.connect(host=config_mysql['host'], port=int(config_mysql['port']), user=config_mysql['user'], passwd=config_mysql['passwd'], db=config_mysql['db'])
    cursor = db.cursor()
    sql_summer = "replace into summer_data(time_t,resolved,new,unresolved) VALUES ('%s','%s','%s','%s')" % (today,resolved_all,new_num,totle_unresolved)
    try:
        cursor.execute(sql_summer)
        db.commit()
        print("ok")
    except:
        # 如果发生错误则回滚
        db.rollback()
        print("no")
    try:
        sql_summer = "SELECT * FROM summer_data WHERE time_t BETWEEN '%s' and '%s'" % (config_Plan['start_time'],config_Plan['end_time'])
        cursor.execute(sql_summer)  # 执行SQL语句
        results_summer = cursor.fetchall()  # 获取所有记录列表
        for row in results_summer:
            time_summer = row[0]
            resolve_summer = row[1]
            new_summer = row[2]
            unresolved_summer = row[-1]
            summer.append([str(time_summer),resolve_summer, new_summer,unresolved_summer])
        print('ok')
    except:
        print("Error: unable to fetch data")
    db.close()
    return summer, daily_row


# 折线图
def chart_line(chart_value,chart_name,img_name):
    x_value=[]
    y1_value,y2_value,y3_value=[],[],[]
    for i in range(1, len(chart_value)):
        if i > 0:
            x_value.append(chart_value[i][0])
            y1_value.append(chart_value[i][1])
            y2_value.append(chart_value[i][2])
            y3_value.append(chart_value[i][3])
    plt.figure(figsize=(17,6))  # 设置画布大小
    plt.grid(axis="y",linestyle='-.') #设置画布背景，横向，虚线
    plt.xticks(rotation=45) #设置x轴展示标签旋转度数
    plt.style.use('ggplot')
    plt.title(chart_name) # 设置图标名称
    line1, =plt.plot(x_value, y1_value,color='#4876FF', marker='*')
    line2, =plt.plot(x_value, y2_value, color='#228B22', marker='*')
    line3, =plt.plot(x_value, y3_value, color='#8B3A62', marker='*')
    plt.legend((line1, line2, line3), ('已解决', '今日新增', '待解决问题'))  # 绘图，并添加标签
    plt.rcParams['font.sans-serif'] = ['simsun']  # 显示中文标签，没有字体
    plt.rcParams['axes.unicode_minus'] = False
    for a, b in zip(x_value, y1_value):
        plt.text
        plt.text(a, b + 0.05, '%.0f' % b, ha='center', va='bottom', fontsize=7)  # 折线添加指标值
    for a, b in zip(x_value, y2_value):
        plt.text
        plt.text(a, b + 0.05, '%.0f' % b, ha='center', va='bottom', fontsize=7)
    for a, b in zip(x_value, y3_value):
        plt.text
        plt.text(a, b + 0.05, '%.0f' % b, ha='center', va='bottom', fontsize=7)
    plt.savefig(img_name+'.png')  # 保存数据到本地
    plt.clf()
    plt.close()
    #plt.show()


def chart_column(chart_value,chart_name,img_name):
    x_value = chart_value[0]
    y_value = chart_value[1]
    plt.bar(x_value[1:], y_value[1:],label='num')
    # plt.figure(figsize=(20, 10))  # 设置画布大小
    plt.grid(axis="y", linestyle='-.')  # 设置画布背景，横向，虚线
    # plt.xticks(rotation=90)  # 设置x轴展示标签旋转度数
    # plt.style.use('ggplot')
    plt.rcParams['font.sans-serif'] = ['simsun']  # 显示中文标签，没有字体
    plt.rcParams['axes.unicode_minus'] = False
    plt.title(chart_name)  # 设置图标名称
    for a, b in zip(x_value[1:], y_value[1:]):
        plt.text
        plt.text(a, b + 0.05, '%.0f' % b, ha='center', va='bottom', fontsize=7)  # 折线添加指标值
    plt.savefig(img_name+'.png')  # 保存数据到本地
    #plt.show()
    plt.clf()
    plt.close()


def chart_barh(chart_value,chart_name,img_name):
    x_value,y_value = [],[]
    for line in chart_value:
        x_value.append(line[0])
        y_value.append(line[1])
    plt.barh(x_value, y_value ,label='num')
    # # plt.figure(figsize=(20, 10))  # 设置画布大小
    plt.grid(axis="x", linestyle='-.')  # 设置画布背景，横向，虚线
    for a, b in zip(x_value, y_value):
        plt.text(b, a, '%d' % int(b), ha='left', va='bottom')  # 折线添加指标值
    plt.title(chart_name)  # 设置图标名称
    plt.savefig(img_name+'.png')  # 保存数据到本地
    #plt.show()
    plt.clf()
    plt.close()


def rm_path():
    import os
    path_list = ['daily_report.html','daily_summary_chart.png','ticet_module_chart.png','ticet_people_chart.png','ticet_resolve_chart.png','ticket_summary_chart.png']
    for path in path_list:
        if os.path.exists(path):
            os.remove(path)
        else:
            print('no such file')  # 返回文件不存在


def write_html():
    person_testrate=current_day()
    condition=analysis()
    daily_summer=SandP_mysql()
    tester_msg = test_rate()
    daily=daily_summer[1]
    #----画图----
    summery_line = daily_summer[0]    # 折线图
    daily_colume = daily_summer[1]    #柱状图
    ticet_people = person_testrate[2]
    ticet_resolve = person_testrate[0]
    ticet_module = person_testrate[1]
    chart_line(summery_line, 'ticket总览', 'ticket_summary_chart')
    chart_column(daily_colume, '今日缺陷状态汇总', 'daily_summary_chart')
    chart_barh(ticet_people, '所有ticket人员对应', 'ticet_people_chart')
    chart_barh(ticet_resolve, '已解决缺陷人员对应', 'ticet_resolve_chart')
    chart_barh(ticet_module, '所有ticket模块对应', 'ticet_module_chart')
    #-----------html生成---------
    file_html = 'daily_report.html'  # html
    with open(file_html, mode='a') as filename:
        filename.write('<html><meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
                       '<body link="blue" vlink="purple">')
        filename.write('<div style="margin-top: 30px">1.测试计划</div>'
                       '<table border="1" cellspacing="0" width="440">'
                       '<tr><td>时间安排</td><td>'+str(config_Plan['test_time'])+'</td></tr>'
                       '<tr><td>测试计划</td><td>'+str(config_Plan['test_plan'])+'</td></tr>'
                       '<tr><td>人员安排</td><td>'+str(config_Plan['tester'])+'</td></tr>'
                       '</table>')
        filename.write('<div style="margin-top: 30px">2.测试版本</div>'
                       '<table border="1" cellspacing="0" width="740">'
                       '<tr><td>序号</td><td>安装日期</td><td>branch</td><td>commit ID</td></tr>'
                       '<tr><td>1</td><td>'+str(person_testrate[-1][0])+'</td><td>'+str(person_testrate[-1][1])+'</td>'
                       '<td>'+str(person_testrate[-1][2])+'</td></tr>'
                       '</table>')
        #   test_rate
        filename.write('<div style="margin-top: 30px">3.测试进度</div><table border="1" cellspacing="0" width="740">'
                       '<tr><td width="100px">模块名称</td><td width="80px">测试人员</td><td width="560px">测试内容及进度</td></tr>')
        for testdate in tester_msg:
            filename.write('<tr><td>'+str(testdate[1])+'</td><td>'+str(testdate[0])+'</td><td>'+str(testdate[2])+'</br>'+str(testdate[3])+'</br>'+str(testdate[4])+'</br>'+str(testdate[5])+'</br></td></tr>')
        filename.write('</table>')
        # -------循环-----
        filename.write('<div style="margin-top: 30px">4.'+str(today)+'今日测试情况</div>')
        filename.write('<table border="1" cellspacing="0" width="140" >'
                       '<tr><td>新增缺陷数</td><td>'+str(summery_line[-1][2])+'</td></tr></table>')
        filename.write('<div style="margin-top: 30px">5.ticket汇总情况</div><div>'
                       '<img src="cid:image1" width="1240px" height="600px"></div>'  #  折线图
                       '<table border="1" cellspacing="0" width="740" style="margin-top: 30px">'
                       '<tr><td>时间</td><td>新建</td><td>进行中</td><td>已解决</td><td>反馈</td><td>阻塞</td><td>推迟</td><td>Reopen</td></tr>'
                       '<tr><td>'+str(daily[1][0])+'</td><td>'+str(daily[1][1])+'</td>'
                       '<td>'+str(daily[1][2])+'</td><td>'+str(daily[1][3])+'</td>'
                       '<td>'+str(daily[1][4])+'</td><td>'+str(daily[1][5])+'</td>'
                       '<td>'+str(daily[1][6])+'</td><td>'+str(daily[1][7])+'</td></tr>'
                       '</table>')
        filename.write('<div style="margin-top: 10px">'
                       '<img src="cid:image2" width="640px" height="400px"></div>' # 柱状图
                       '<table border="1" cellspacing="0" width="740" style="margin-top: 30px"><tr>'
                       '<td>超过一周未更新</td><td>'+str(condition[5])+'</td><td>退化的ticket数</td><td>'+str(condition[-2])+'</td>'
                       '<td>致命/重大ticket数</td><td>'+str(condition[3])+'</td><td>已解决缺陷</td><td>'+str(condition[4])+'</td>'
                       '<td>今日新建数</td><td>'+str(summery_line[-1][2])+'</td></tr></table>')

        filename.write('<div style="margin-top: 30px">6.缺陷概况</div><div style="margin-top: 2px">')
        filename.write('<div style="margin-top: 2px">阻塞问题列表</div><table border="1" cellspacing="0" width="740">'
                       '<tr><td>序号</td><td>指派给</td><td>状态</td><td>ticket_ID</td><td>ticket详情</td></tr>')
        if condition[1]:
            for s,stop in enumerate(condition[1]):
                filename.write('<tr><td>' + str(s+1) + '</td><td>' + str(stop[0]) + '</td><td>' + str(
                    stop[1]) + '</td><td>' + str(stop[2]) + '</td><td>' + str(stop[3]) + '</td></tr>')
        filename.write('</table>')
        filename.write('<div style="margin-top: 10px">严重问题列表</div><table border="1" cellspacing="0" width="740">'
                       '<tr><td>序号</td><td>指派给</td><td>状态</td><td>ticket_ID</td><td>ticket详情</td></tr>')
        if condition[0]:
            for p,perish in enumerate(condition[0]):
                filename.write('<tr><td>' + str(p+1) + '</td><td>' + str(perish[0]) + '</td><td>' + str(perish[1]) + '</td><td>' + str(perish[2]) + '</td><td>' + str(perish[3]) + '</td></tr>')
        filename.write('</table>')
        filename.write('<div style="margin-top: 10px">退化问题列表</div><table border="1" cellspacing="0" width="740">'
                       '<tr><td>序号</td><td>指派给</td><td>状态</td><td>ticket_ID</td><td>ticket详情</td></tr>')
        if condition[-1]:
            for b,back in enumerate(condition[-1]):
                filename.write('<tr><td>'+str(b+1) +'</td><td>'+str(back[0])+'</td><td>'+str(back[1])+'</td><td>'+str(back[2])+'</td><td>'+str(back[3])+'</td></tr>')
        filename.write('</table>')
        filename.write('<div style="margin-top: 30px">7.所有缺陷人员对应</div><div style="margin-top: 2px">'
                       '<img src="cid:image3" width="640px" height="400px"></div>' # 所有缺陷人员对应
                       '<div style="margin-top: 30px">8.已解决缺陷人员对应</div><div style="margin-top: 2px">'
                       '<img src="cid:image4" width="640px" height="400px"></div>' # 已解决缺陷人员对应
                       '<div style="margin-top: 30px">9.所有缺陷模块对应</div><div style="margin-top: 2px">'
                       '<img src="cid:image5" width="640px" height="400px"></div>') # 所有缺陷模块对应
        filename.write('</body></html>')


if __name__ == '__main__':
    redmine = Redmine(config_Redmine['host'], username=config_Redmine['username'], password=config_Redmine['pw'])
    project_name = redmine.project.get(config_Redmine['project_name'])
    issues_open = list(redmine.issue.filter(project_id=project_name.id, tracker_id=1, status_id='o', set_filter=1, fixed_version_id=config_Redmine['fixed_version_id']))
    issues_all = list(redmine.issue.filter(project_id=project_name.id, tracker_id=1, set_filter=1, status_id='*', fixed_version_id=config_Redmine['fixed_version_id']))
    time = datetime.now().timetuple()
    today = str(time.tm_year) + '-' + str(time.tm_mon) + '-' + str(time.tm_mday)
    rm_path()  # 清理已生成的文件
    write_html()