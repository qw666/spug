
import React, { useState, useEffect } from 'react';
import {observer} from "mobx-react";
import store from "./store";
import http from 'libs/http';
import styles from './index.module.less';
import {Form, Input, Modal, Row, Col, Select, Button, Divider, Radio, Space, Cascader, message} from "antd";
import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons';
import SQLTable from "./SQLTable";
import {toJS} from "mobx"
import lds from "lodash";
//引入antd组件内的组件的时候要放到最下边 要不有的报错 比如TextArea
const { TextArea } = Input;
const { Option } = Select;
export default observer(function () {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false);
    const [gcoptions, setgcOptions] = useState([]);
    const [sqloptions, setsqlOptions] = useState([]);
    const [errorCount, setErrorCount] = useState(-1);

    useEffect(() => {
        fetchProject();
        getSqlType();

        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);
    function getSqlType() {
        http.get('/api/gh/archery/instance?status='+"" ).then(res => {
            const optionSqlLists = [];
            let sqlData = res;
            console.log("sqlData",sqlData);
            for (let i = 0; i < sqlData.length; i++) {
                optionSqlLists.push({
                    value:sqlData[i].db_type,
                    label: sqlData[i].db_type,
                    id: sqlData[i].id,
                    resource_group:sqlData[i].resource_group,
                    isLeaf: false,
                })
            }
            setsqlOptions(optionSqlLists);
        })
        //数据库动态加载级联数据

    }
    const SQLInspect = ()=>{
        setErrorCount(-1)
    }
    function fetchProject() {
        http.get('/api/gh/app/listApps/').then(res => {
            let gcData = res;
            let optionGCLists = [];
            console.log("gcData",gcData);
            for (let i = 0; i < gcData.length; i++) {
                optionGCLists.push({
                    value:gcData[i].name,
                    label: gcData[i].name,
                    deploy_id:gcData[i].deploy_id,//需要请求2级工程的字段
                    isLeaf: false,
                })
            }
            setgcOptions(optionGCLists);
        })
    }
    const gcloadData = (selectedOptions) => {
        const targetOption = selectedOptions[selectedOptions.length - 1];
        let deploy_id = targetOption.deploy_id;
        console.log("targetOption",targetOption);
        targetOption.loading = true;
        http.get('/api/gh/app/deploy/133/versions/?deploy_id= ' + deploy_id ).then(res => {
            console.log(res);
            // load options lazily
            setTimeout(() => {
                targetOption.loading = false;
                let data = res;
                targetOption.children = [];
                let val = Object.keys(data.branches);
                for (let i = 0; i < val.length; i++) {
                    targetOption.children.push({
                        label: val[i],
                        value: val[i]
                    })
                }
                console.log("targetOption",targetOption);
                setgcOptions([...gcoptions]);
            }, 2000);
        })
    };



    const sqlonChange = (value, selectedOptions) => {
        console.log(value, selectedOptions);
    };
    const sqlloadData = (selectedOptions) => {
        const targetOption = selectedOptions[selectedOptions.length - 1];
        console.log("targetOption",targetOption);
        targetOption.loading = true;
        http.get('/api/gh/archery/resource',{
            params:{
                instance_id:targetOption.id,
                status:""
            }
        }).then(res => {
            setTimeout(() => {
                targetOption.loading = false;
                let data = res
                targetOption.children = [];
                for (let i = 0; i < data.length; i++) {
                    targetOption.children.push({
                        label: data[i],
                        value: data[i]
                    })
                }

                setsqlOptions([...sqloptions]);
            }, 1000);
        })
        // load options lazily

    };
    //表单提交
    function handleSubmit() {
        const formData = form.getFieldsValue();
        console.log(formData);
        if(formData.developer_name){
            formData.developer_name = formData.developer_name.toString();
        }
        if(formData.tester_name){
            formData.tester_name = formData.tester_name.toString();
        }
        let projects = formData.projects;
        if(projects){
            for (let i = 0; i < projects.length; i++) {
                 for (let j = 0; j < gcoptions.length; j++) {
                     if(projects[i].projectsName.length == 2){
                         if(projects[i].projectsName[0] == gcoptions[j].value){
                             projects[i].app_name = projects[i].projectsName[0];
                             projects[i].branch_name = projects[i].projectsName[1];
                             projects[i].deploy_id = gcoptions[j].deploy_id;
                         }
                     }else{
                         return message.error('请选择正确的工程信息/分支信息')
                     }
                 }
             }
         }else{
            return message.error('请添加工程信息')
        }

        let databases = formData.databases;
        console.log("databases",databases);
        if(databases){
            for (let i = 0; i < databases.length; i++) {
                for (let j = 0; j < sqloptions.length; j++) {
                    console.log(databases[i].databasesName.length);
                    if(databases[i].databasesName.length == 2){
                        console.log(databases[i].databasesName[0], sqloptions[j]);
                        if(databases[i].databasesName[0] == sqloptions[j].value){
                            databases[i].db_type = databases[i].databasesName[0];
                            databases[i].instance = sqloptions[j].id;
                            databases[i].db_name = databases[i].databasesName[1];
                            databases[i].group_id = sqloptions[j].resource_group[0];
                        }
                    }else{
                        return message.error('请选择正确的数据库类型/数据库名称')
                    }

                }
            }
        }else{
            return message.error('请添加数据库配置')
        }
        if(errorCount !== 0){
            return message.error('请SQL检查')
        }
        http.post('/api/gh/test/', formData).then((res)=>{
            if(res == "success"){
                message.success('操作成功');
                store.fetchRecords();
                store.addVisible = false;
            }
        })
    }
    function handleInspct() {
        let formData = form.getFieldsValue();

        let databases = formData.databases;
        console.log("databases",databases);
        if(databases){
            for (let i = 0; i < databases.length; i++) {
                for (let j = 0; j < sqloptions.length; j++) {
                    console.log(databases[i].databasesName.length);
                    if(databases[i].databasesName.length == 2){
                        console.log(databases[i].databasesName[0], sqloptions[j]);
                        if(databases[i].databasesName[0] == sqloptions[j].value){
                            databases[i].db_type = databases[i].databasesName[0];
                            databases[i].instance = sqloptions[j].id;
                            databases[i].db_name = databases[i].databasesName[1];
                            databases[i].group_id = sqloptions[j].resource_group[0];
                        }
                    }else{
                        return message.error('请选择正确的数据库类型/数据库名称')
                    }

                }
            }
        }else{
            return message.error('请添加数据库配置')
        }

        let temp = [];
        http.post('/api/gh/archery/check',{
            databases:databases
        }).then((res)=>{
            let data = res;
            setErrorCount(data.error_count);
            store.SqlErrorTable = data.error_group;
            store.SqlWarnTable =data.warning_group;
            if(data.error_count === 0){
                message.success('操作成功')
            }
        })

       /* this.SqlWarnTable = Object.values(toJS(temp))
        this.SqlErrorTable = Object.values(toJS(temp))*/

        //console.log(this.SqlErrorTable);
        //this.error_count = 0;  //0的话可以提交表单 其余不可以提交
    }
    function handleReset() {
        form.resetFields();
    }
    return (
        <Modal
            visible
            width={800}
            maskClosable={false}
            title={store.formType === "add"?"新建申请":store.formType === "look"?"查看申请":""}
            onCancel={() => store.addVisible = false}
            confirmLoading={loading}
            onOk={handleSubmit}
            footer={
                store.formType === "add" ?
                    [
                        <Button
                            type="primary"
                            key="cancel"
                            onClick={handleInspct}
                        >
                            SQL检查
                        </Button>,
                        <Button
                            type="primary"
                            key="ok"
                            onClick={handleSubmit}
                        >
                            提交
                        </Button>,
                        <Button
                            type="primary"
                            key="ok"
                            onClick={handleReset}
                        >
                            重置
                        </Button>
                    ]
                    :[]}
        >
                <Form
                    form={form}
                    initialValues={store.addForm}
                    labelCol={{span: 6}}
                    wrapperCol={{span: 18}}>
                <Row>
                    <Col span={11}>
                        <Form.Item  required name="demand_name" label="需求名称" >
                            <Input disabled={store.formType === "look"} placeholder="请输入需求名称"/>
                        </Form.Item>
                    </Col>
                    <Col span={11}>
                        <Form.Item   required name="demand_link" label="需求链接" >
                            <Input disabled={store.formType === "look"} placeholder="请输入需求链接"/>
                        </Form.Item>
                    </Col>
                </Row>
                <Row>
                    <Col span={11}>
                        <Form.Item  required name="developer_name" label="开发人员" >
                            <Select
                                mode="multiple"
                                allowClear
                                disabled={store.formType === "look"}
                                placeholder="请选择开发人员">
                                {store.developersList.map( (item,index )    => (
                                    <Select.Option value={item.nickname} key={index}>{item.nickname}</Select.Option>
                                ))}
                            </Select>
                        </Form.Item>
                    </Col>
                    <Col span={11}>
                        <Form.Item   required name="tester_name" label="测试人员" >
                            <Select
                                mode="multiple"
                                disabled={store.formType === "look"}
                                allowClear
                                placeholder="请选择测试人员">
                                {store.testersList.map(item => (
                                    <Select.Option value={item.nickname} key={item.nickname}>{item.nickname}</Select.Option>
                                ))}
                            </Select>
                        </Form.Item>
                    </Col>
                </Row>
                <Form.List name="projects"  initialValue={store.addFormProjects}>
                    {(fields, { add, remove }) => (
                        <>
                            {fields.map((field,index) => (

                                <Row key={field.key} align="baseline">
                                    <Col span={22} >
                                        <Form.Item
                                            shouldUpdate={(prevValues, curValues) => prevValues.projectsName !== curValues.projectsName}
                                            labelCol={{span: 3}} wrapperCol={{span: 21}}
                                            {...field}
                                            label="工程信息"
                                            name={[field.name, 'projectsName']}
                                            required
                                        >
                                            <Cascader
                                                disabled={store.formType === "look"}
                                                placeholder="请选择工程信息/分支信息"
                                                options={gcoptions}
                                                loadData={gcloadData}
                                                changeOnSelect />
                                        </Form.Item>
                                    </Col>

                                    <Col span={2}>
                                        {store.formType === "add" &&  <MinusCircleOutlined  className={styles.MinusCircleOutlined}    onClick={() => remove(field.name)} />}

                                    </Col>

                                </Row>

                            ))}
                            {store.formType === "add" &&  <Form.Item>
                                <Button className={styles.addGcBtn} type="dashed"  onClick={() => add()}  block icon={<PlusOutlined />}>
                                    添加工程信息
                                </Button>
                            </Form.Item>}

                        </>
                    )}
                </Form.List>
                <Divider/>
                <Form.List name="databases" initialValue={store.addFormDatabases}>
                    {(fields, { add, remove }) => (
                        <>

                            {
                                fields.map((field,index) => (
                                <Form.Item
                                    key={field.key}
                                    noStyle
                                >
                                    <Row  align="baseline">
                                        <Col span={22} >
                                            <Form.Item
                                                labelCol={{span: 3}} wrapperCol={{span: 12}}
                                                {...field}
                                                label="数据库"
                                                name={[field.name, 'databasesName']}
                                                required
                                            >
                                                <Cascader  style={{marginLeft:"10px"}}
                                                           disabled={store.formType === "look"}
                                                           placeholder="请选择数据库类型/数据库名称"
                                                           options={sqloptions}
                                                           loadData={sqlloadData}
                                                           onChange={sqlonChange}
                                                           changeOnSelect />
                                            </Form.Item>
                                        </Col>
                                        <Col span={2}>
                                            {store.formType === "add" &&
                                            <MinusCircleOutlined  className={styles.MinusCircleOutlined}    onClick={() => remove(field.name)} />}

                                        </Col>
                                    </Row>
                                    <Row  align="baseline">

                                        <Col span={22} >
                                            {store.formType == "add"?<Form.Item
                                                labelCol={{span: 3}} wrapperCol={{span: 9}}
                                                {...field}
                                                label="Sql类型"
                                                name={[field.name, 'sql_type']}
                                                required
                                            >
                                                <Space size="Large"   style={{marginLeft:"10px"}}>
                                                    <Radio.Group   disabled={store.formType === "look"}>
                                                        <Radio value={1}>DDL</Radio>
                                                        <Radio value={2}>DML</Radio>
                                                    </Radio.Group>
                                                </Space>

                                            </Form.Item>:<Form.Item
                                                labelCol={{span: 3}} wrapperCol={{span: 9}}
                                                {...field}
                                                label="Sql类型"
                                                name={[field.name, 'sql_type']}
                                                required
                                            >
                                                <Space size="Large"    style={{marginLeft:"10px"}}>
                                                    <Radio.Group value={store.addForm.databases[index].sql_type}>
                                                        <Radio disabled={store.formType === "look"} value={1}>DDL</Radio>
                                                        <Radio disabled={store.formType === "look"} value={2}>DML</Radio>
                                                    </Radio.Group>
                                                </Space>
                                            </Form.Item>}
                                        </Col>
                                    </Row>
                                    <Row  align="baseline">
                                        <Col span={22} >
                                            <Form.Item
                                                labelCol={{span: 3}} wrapperCol={{span: 15}}
                                                {...field}
                                                label="Sql内容"
                                                name={[field.name, 'sql_content']}
                                                required
                                            >
                                                <TextArea   onChange={SQLInspect}  disabled={store.formType === "look"} style={{marginLeft:"10px"}} rows={4} />

                                            </Form.Item>
                                        </Col>
                                    </Row>
                                    <Divider/>
                                </Form.Item>
                            ))}
                            {store.formType === "add" && <Form.Item>
                                <Button className={styles.addGcBtn} type="dashed"  onClick={() => add()}  block icon={<PlusOutlined />}>
                                    添加数据库配置
                                </Button>
                            </Form.Item> }


                            {store.formType === "add" ?<SQLTable form={form}/>   : null}
                        </>
                    )}
                </Form.List>
            </Form>
        </Modal>
    )
})