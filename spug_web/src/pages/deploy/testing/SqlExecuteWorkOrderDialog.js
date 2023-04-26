import React, { useState, useEffect } from 'react';
import {observer} from "mobx-react";
import store from "./store";
import styles from './index.module.less';
import {Form, Input, Modal, Row, Col, Select, Divider, Radio, Space, Cascader, Table, Popover} from "antd"
import SQLTable from "./SQLTable";
//引入antd组件内的组件的时候要放到最下边 要不有的报错 比如TextArea
const { TextArea } = Input;
const { Option } = Select;
export default observer(function () {
    const [form] = Form.useForm();
    //表单提交
    function HandleSubmit() {
        const formData = form.getFieldsValue();
        console.log(formData);
    }
    const onChange = (e)=>{
        console.log(e.target.value);
    }

    const optionSqlLists = [];
    let sqlData = [
        {
            "id": 2,//一级的value
            "instance_name": "test-mysql",
            "db_type": "mysql", //一级label
            "resource_group": [
                2
            ]
        }
    ]
    for (let i = 0; i < sqlData.length; i++) {
        optionSqlLists.push({
            value:sqlData[i].db_type,
            label: sqlData[i].db_type,
            isLeaf: false,
        })
    }

    const [sqloptions, setsqlOptions] = useState(optionSqlLists);
    const sqlonChange = (value, selectedOptions) => {
        console.log(value, selectedOptions);
    };
    const sqlloadData = (selectedOptions) => {
        const targetOption = selectedOptions[selectedOptions.length - 1];
        console.log("targetOption",targetOption);
        targetOption.loading = true;
        // load options lazily
        setTimeout(() => {
            targetOption.loading = false;
            let data = [
                "gh_cloud_biz",
                "gh_cloud_biz_1hgs",
                "gh_cloud_biz_baohe",
                "gh_cloud_biz_test230",
                "gh_cloud_biz_test231",
                "gh_cloud_biz_test232",
                "gh_cloud_biz_test233",
                "gh_cloud_biz_test234",
            ]
            targetOption.children = [];
            for (let i = 0; i < data.length; i++) {
                targetOption.children.push({
                    label: data[i],
                    value: data[i]
                })
            }

            setsqlOptions([...sqloptions]);
        }, 1000);
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
                                                           onChange={sqlonChange}
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
                                               {store.sqlExecuteWorkOrderForm.databases[index].sql_type}
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