import React, { useState, useEffect } from 'react';
import {observer} from "mobx-react";
import store from "./store";
import http from 'libs/http';
import styles from './index.module.less';
import {Form, Input, Modal, Row, Col, Select, Divider, Radio, Space, Cascader, Table, Popover, message} from "antd"
import SQLTable from "./SQLTable";
//引入antd组件内的组件的时候要放到最下边 要不有的报错 比如TextArea
const { TextArea } = Input;
const { Option } = Select;
export default observer(function () {
    const [sqloptions, setsqlOptions] = useState([]);
    const [form] = Form.useForm();
    useEffect(() => {
        getSqlType();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    function getSqlType() {
        http.get('/api/gh/archery/instance',{
            params: {
                status:store.sqlExecuteWorkOrderForm.status
            }
        }).then(res => {
            const optionSqlLists = [];
            let sqlData = res;
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

    //表单提交
    function HandleSubmit() {
        const formData = form.getFieldsValue();
        formData.id = store.sqlExecuteWorkOrderForm.id;
        formData.demand_link = store.sqlExecuteWorkOrderForm.demand_link;
        formData.sql_exec_status = store.sqlExecuteWorkOrderForm.sql_exec_status;
        formData.status = store.sqlExecuteWorkOrderForm.status;

        if(formData.developer_name){
            formData.developer_name = formData.developer_name.toString();
        }
        if(formData.tester_name){
            formData.tester_name = formData.tester_name.toString();
        }
        let databases = formData.databases;
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
        console.log(formData);
        http.post('/api/gh/archery/resource',formData).then(res=>{
            store.fetchRecords();
            store.sqlVisible = false;
        })
    }

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
    return(
        <Modal
            visible
            width={600}
            maskClosable={false}
            title={store.sqlExecuteWorkOrderFormType === "xs"?"SQL线上执行":"SQL测试执行"}
            onCancel={() => store.sqlVisible = false}
            onOk={HandleSubmit}>
            <Form form={form} initialValues={store.sqlExecuteWorkOrderForm} labelCol={{span: 5}} wrapperCol={{span: 17}}>
                <Row>
                    <Col span={22}>
                        <Form.Item labelCol={{span: 4}} wrapperCol={{span: 20}} required name="demand_name" label="需求名称" >
                            <Input disabled placeholder="请输入需求名称"/>
                        </Form.Item>
                    </Col>
                </Row>
                <Row>
                    <Col span={22}>
                        <Form.Item  labelCol={{span: 4}} wrapperCol={{span: 20}}  required name="developer_name" label="开发人员" >
                            <Select
                                disabled
                                mode="multiple"
                                allowClear
                                placeholder="请选择">
                                {store.developersList.map( (item,index )    => (
                                    <Select.Option value={item.nickname} key={index}>{item.nickname}</Select.Option>
                                ))}
                            </Select>
                        </Form.Item>
                    </Col>
                </Row>
                <Row>
                    <Col span={22}>
                        <Form.Item  labelCol={{span: 4}} wrapperCol={{span: 20}}  required name="tester_name" label="测试人员" >
                            <Select
                                disabled
                                mode="multiple"
                                allowClear
                                placeholder="请选择">
                                {store.testersList.map(item => (
                                    <Select.Option value={item.nickname} key={item.nickname}>{item.nickname}</Select.Option>
                                ))}
                            </Select>
                        </Form.Item>
                    </Col>
                </Row>
                <Divider/>
                <Form.List name="databases" initialValues={store.sqlExecuteWorkOrderForm.databases}>
                    {(fields, { add, remove }) => (
                        <>
                            {fields.map((field,index) => (

                                <Form.Item
                                    key={field.key}
                                    noStyle
                                >
                                    <Row  align="baseline">
                                        <Col span={22} >
                                            <Form.Item
                                                labelCol={{span: 4}} wrapperCol={{span: 20}}
                                                {...field}
                                                label="数据库"
                                                name={[field.name, 'databasesName']}
                                                required
                                                extra={<span  >
                                                    请重新选择数据库 {store.sqlExecuteWorkOrderForm.databases[index].db_type +" / "+
                                                store.sqlExecuteWorkOrderForm.databases[index].db_name}</span>}
                                            >
                                                <Cascader
                                                           placeholder="请选择数据库类型/数据库名称"
                                                           options={sqloptions}
                                                           loadData={sqlloadData}
                                                           changeOnSelect />
                                            </Form.Item>
                                        </Col>
                                    </Row>
                                    <Row  align="baseline">
                                        <Col span={22} >
                                            <Form.Item
                                                labelCol={{span: 4}} wrapperCol={{span: 20}}
                                                {...field}
                                                label="Sql类型"
                                                name={[field.name, 'sql_type']}
                                                required
                                            >
                                                <Space size="Large"  >
                                                    <Radio.Group
                                                        onChange={ (e)=>{
                                                            form.setFieldsValue({
                                                                sql_type:e.target.value
                                                            });
                                                            store.sqlExecuteWorkOrderForm.databases[index].sql_type = e.target.value
                                                        }}
                                                        value={store.sqlExecuteWorkOrderForm.databases[index].sql_type}
                                                    >
                                                        <Radio value={1}>DDL</Radio>
                                                        <Radio value={2}>DML</Radio>
                                                    </Radio.Group>
                                                </Space>

                                            </Form.Item>
                                        </Col>
                                    </Row>
                                    <Row  align="baseline">
                                        <Col span={22} >
                                            <Form.Item
                                                labelCol={{span: 4}} wrapperCol={{span: 20}}
                                                {...field}
                                                label="Sql内容"
                                                name={[field.name, 'sql_content']}
                                                required
                                            >
                                                <TextArea   rows={4} />

                                            </Form.Item>
                                        </Col>
                                    </Row>
                                    <Divider/>
                                </Form.Item>
                            ))}
                        </>
                    )}
                </Form.List>
            </Form>
        </Modal>
    )
})