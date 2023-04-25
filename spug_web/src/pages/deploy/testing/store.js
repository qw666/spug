import { observable, computed} from "mobx";
import http from 'libs/http';
import {message, Modal} from "antd";
import {toJS} from "mobx"
import lds from "lodash";

class Store {
    @observable projectOneLevelList = [];
    @observable sqlTypeList = [];
    @observable f_status = 'all';
    @observable formType = "add";
    @observable error_count = -1;
    @observable appointType = "test";//指定弹框类型 是指定测试test 还是指定上线 goOnline
    //table初始数据做过滤处理 实际表格数据参数为 dataSource
    @observable tableData = [];

    @observable addForm = {

    };//表单属性
    @observable addFormProjects = [{projectsName:""}]
    @observable addFormDatabases = []
    @observable counter = {};//表格标签按钮
    @observable tabs = [];

    @observable f_s_date;//开始时间
    @observable f_e_date;//结束时间

    @observable requirementNameList = [];//需求名称列表


    @observable requirementName;//需求名称
    //开发人员列表
    @observable developersList = [];
    //测试人员列表
    @observable testersList = [];
    //全部人员列表 测试 开发等
    @observable allList =  [];
    @observable developers;//开发人员
    @observable demand_name;//需求名称

    @observable testers;//测试人员

    @observable isFetching = false;
    @observable addVisible = false;//新建申请和查看弹框
    @observable SqlWarnTable = [];//Sql检索警告表格数据
    @observable SqlErrorTable = [];//Sql检索错误表格数据

    @observable appointVisible = false; //指定 弹框
    @observable appointForm = {};//指定表单属性

    @observable sqlVisible = false; //sql执行工单弹框
    @observable sqlExecuteWorkOrderForm = {};//sql执行表单属性
    @observable sqlExecuteWorkOrderFormType = "zx";//zx在线执行 lx测试执行
    //table数据
    @computed get dataSource() {
        let data = Object.values(toJS(this.tableData))
        //table过滤开发人员
        if (this.developers){
            data = data.filter((x)=>{
                if(toJS(x.developer_name).split(",").includes(this.developers)){
                    return x
                }
            })
        }
        if (this.demand_name) data = data.filter(x => x.demand_name.toLowerCase().includes(this.demand_name.toLowerCase()));
        if (this.f_s_date) data = data.filter(x => {
            const date = x.created_at.substr(0, 10);
            return date >= this.f_s_date && date <= this.f_e_date
        });
        if (this.f_status !== 'all') {
            data = data.filter(x => x.status == this.f_status)
        }
        return data
    }
    @observable testsCompleteVisible = false;//测试完成弹框
    @observable testsCompleteForm = {};//测试完成表单
    @observable synchronousEnvVisible = false;//同步测试环境弹框
    @observable synchronousEnvForm = { }; //同步测试环境表单
    @observable synchronousEnvList = [
        {label:"测试环境230",value:"test230"},
        {label:"测试环境231",value:"test231"},
        {label:"测试环境232",value:"test232"},
        {label:"测试环境233",value:"test233"},
    ];//同步环境列表
    @observable synchronousEnvTableData = [{
        street1:'111',
        status:0
    }];//表格数据
    @observable reloadSqlVisible = false;//重新执行sql弹框
    @observable reloadSqlform = {};//重新执行sql内容表单


    @computed get sqlDataSource() {
        let data = Object.values(toJS(this.SqlTable))
        return data
    }
    //表格数据请求
    fetchRecords = () => {
        this.isFetching = true;
        http.get('/api/gh/test/')
            .then(res => {

                for (let i = 0; i < res.length; i++) {
                    console.log(res[i]);
                    let databases = res[i].databases;
                    for (let j = 0; j < databases.length; j++) {
                        databases[j].databasesName = [databases[j].db_type,databases[j].db_name]
                    }
                    let projects = res[i].projects;
                    for (let j = 0; j < projects.length; j++) {
                        projects[j].projectsName = [projects[j].app_name,projects[j].branch_name]
                    }
                }
                this.tableData = res
                console.log(res);
            })
            .then(this._updateCounter)
            .finally(() => this.isFetching = false)
    };
    //获取测试人员
    getTesterList = () =>{
        http.get('/api/gh/user/listUsers/?role_type=2').then(res => {
                this.testersList = res
        })
    };
    //获取开发人员
    getDevelopersList = () =>{
        http.get('/api/gh/user/listUsers/?role_type=1').then(res => {
            this.developersList = res
        })
    };
    //获取全部人员
    getAllPersonnel = () =>{
        http.get('/api/gh/user/listUsers/?role_type=3').then(res => {
            this.allList = res
        })
    };
    //新建申请
    addDialog = ()=>{
        this.addForm = {};
        this.formType = "add";
        /*this.addFormProjects = [{
            projectsName:[ ]
        }]*/
     /*   this.getProjectLevelOne();
        this.getSqlType("");*/
        this.addVisible = true;
       /* setTimeout(()=>{

        },500)*/

    };
    //查看 和新建申请一个表单
    lookDialog = (e,info)=>{
        console.log(info);
        if(!Array.isArray(info.developer_name)){
            info.developer_name = info.developer_name.split(",");
        }
        if(!Array.isArray(info.tester_name)){
            info.tester_name = info.tester_name.split(",");
        }
        if (e) e.stopPropagation();
        this.formType = "look";
        this.addVisible = true;
        this.addForm = info;
        console.log("this.addForm",this.addForm);


    };
    //重新测试
    retest = (e,info) =>{
        Modal.confirm({
            title: '重新测试确认',
            content: `确定要重新测试【${info['demand_name']}】?`,
            onOk: () => {
                return http.delete('/api/deploy/request/', {params: {id: info.id}})
                    .then(() => {
                        message.success('操作成功');
                        //表格数据请求
                        this.fetchRecords()
                    })
            }
        })
    };
    //上线
    goOnline = (info) =>{
        Modal.confirm({
            title: '上线确认',
            content: `确定要上线【${info['demand_name']}】?`,
            onOk: () => {
                return http.delete('/api/deploy/request/', {params: {id: info.id}})
                    .then(() => {
                        message.success('操作成功');
                        //表格数据请求
                        this.fetchRecords()
                    })
            }
        })
    };
    //运维上线
    ywgoOnline = (e,info) =>{
        Modal.confirm({
            title: '运维上线确认',
            content: `确定要运维上线【${info['demand_name']}】?`,
            onOk: () => {
                return http.delete('/api/deploy/request/', {params: {id: info.id}})
                    .then(() => {
                        message.success('操作成功');
                        //表格数据请求
                        this.fetchRecords()
                    })
            }
        })
    };
    //上线完成
    onlineCompletion = (e,info) =>{
        Modal.confirm({
            title: '上线完成确认',
            content: `确定要上线完成【${info['demand_name']}】?`,
            onOk: () => {
                return http.delete('/api/deploy/request/', {params: {id: info.id}})
                    .then(() => {
                        message.success('操作成功');
                        //表格数据请求
                        this.fetchRecords()
                    })
            }
        })
    };
     handleDelete = (info) => {
        Modal.confirm({
            title: '删除确认',
            content: `确定要删除【${info['demand_name']}】?`,
            onOk: () => {
                return http.delete('/api/deploy/request/', {params: {id: info.id}})
                    .then(() => {
                        message.success('删除成功');
                        //表格数据请求
                        this.fetchRecords()
                    })
            }
        })
    };
     //指定弹框
    appointDialog(info,type){
         this.appointType = type;
         this.appointVisible = true;
        if(!Array.isArray(info.developer_name)){
            info.developer_name = info.developer_name.split(",");
        }
        if(!Array.isArray(info.tester_name)){
            info.tester_name = info.tester_name.split(",");
        }
         this.appointForm = info
     }
     //sql执行工单
    sqlExecuteWorkOrder(info,type){
        //需要重新请求一级数据库 带状态区分当前是测试还是开发
        let status = info.status;

        delete info.projects;
        if(!Array.isArray(info.developer_name)){
            info.developer_name = info.developer_name.split(",");
        }
        if(!Array.isArray(info.tester_name)){
            info.tester_name = info.tester_name.split(",");
        }
        for (let i = 0; i < info.databases.length; i++) {
            info.databases[i].databasesName = []; //数据库级联不显示数据 需要操作
        }
        this.sqlVisible = true;
        this.sqlExecuteWorkOrderFormType = type;
        this.sqlExecuteWorkOrderForm = info;

        let par = lds.cloneDeep(info);

        par.tester_name = par.tester_name.toString();
        par.developer_name = par.tester_name.toString();
        console.log("info",info);
        console.log(par);
    };
    //表格 tag状态数值
    _updateCounter = () => {
        const counter = {'all': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0};
        for (let item of this.tableData) {
            counter['all'] += 1;
            counter[item['status']] += 1
        }
        this.counter = counter
    };
    testsOk = (info) =>{
        this.testsCompleteVisible = true;
        if(!Array.isArray(info.developer_name)){
            info.developer_name = info.developer_name.split(",");
        }
        if(!Array.isArray(info.tester_name)){
            info.tester_name = info.tester_name.split(",");
        }
        this.testsCompleteForm = info;
    };
    //时间Change
    updateDate = (data) => {
        if (data && data.length === 2) {
            this.f_s_date = data[0].format('YYYY-MM-DD');
            this.f_e_date = data[1].format('YYYY-MM-DD')
        } else {
            this.f_s_date = null;
            this.f_e_date = null
        }
    };
    //获取工程一级数据
    getProjectLevelOne = () =>{
        http.get('/api/gh/app/listApps/').then(res => {
            this.projectOneLevelList = res;
        })
    };
    //获取数据库级联 一级数据  根据状态请求
    getSqlType = (status) =>{
        http.get('/api/gh/archery/instance?status=' + status).then(res => {
            this.sqlTypeList = res;
        })
    };
    //获取数据库级联 二级数据
    getSqlName = (id) =>{
        http.get('/api/gh/archery/resource?instance_id' + id).then(res => {

        })
    };
    //sql检查
    getSqlIinspect = (data) =>{
        http.post('/api/gh/archery/check/',{
            data
        }).then(res => {

        })
    };
    //同步测试环境
    synchronousEnv = (info) =>{
        this.synchronousEnvForm = info;
        this.synchronousEnvForm.sync_env = ["test230"];
        this.synchronousEnvTableData = [{
            "db_type": "mysql",
            "instance": 1,
            "db_name": "gh_cloud_sys_test230",
            "group_id": 2,
            "sql_type": 1,
            "sql_content": "mysql",
            "status": 2
    }];
        this.synchronousEnvGetData(info);
        this.synchronousEnvVisible = true;

    };
    //同步测试环境 查询接口
    synchronousEnvGetData = (info)=>{
        http.get('/api/gh/archery/sync?id' + info.id).then(res => {
            this.synchronousEnvForm.sync_env = res.sync_complete;
            this.synchronousEnvTableData = res.execute_record;
        })
    }
    reloadSqlCont = (info)=>{
       this.reloadSqlVisible = true;
    }

}

export default new Store()