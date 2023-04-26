import React from 'react';
import { observer } from 'mobx-react';
import {Col, Divider, Form, Input, message, Modal, Row, Select, Table, Tag} from "antd";
import store from "./store";
import { Action } from 'components';
import S from "./index.module.less";
import http from 'libs/http';
const { TextArea } = Input;

function SynchronousEnv(props) {
    const [form] = Form.useForm();
    const [reloadSqlform] = Form.useForm();
    //表单提交
    const HandleSubmit = () => {
        const formData = form.getFieldsValue();
        console.log(formData);
        http.post('/api/gh/archery/sync/',{
           id:store.synchronousEnvForm.id,
            demand_name:formData.demand_name,
            demand_link:formData.demand_link,
            sync_env:formData.sync_env.toString(),
            sync_complete:formData.sync_complete.toString(),
        }).then(res => {

        })
    };
    //重新执行
    const reloadSqlSumbit= () => {
        const reloadSqlformData = reloadSqlform.getFieldsValue();
        console.log(store.synchronousEnvForm.id);
        console.log(reloadSqlformData);
        http.patch('/api/gh/archery/sync/', {
            id: store.synchronousEnvForm.id,
            sql_content: reloadSqlformData.sql_content
        }).then(() => {
                message.success('操作成功');
                store.synchronousEnvGetData(store.synchronousEnvForm);
        })
    };
    const tableColumns = [
        {
            title: '数据库类型',
            dataIndex: 'db_type',
            key: 'db_type',
            editable:true,
            width: 120,
        },
        {
            title: '数据库名称',
            dataIndex: 'db_name',
            key: 'db_name',
            width: 180,
        },
        {
            title: 'sql类型',
            key: 'sql_type',
            width: 100,
            render: info => {
                switch (info.sql_type) {
                    case 1:
                        return "DDL";
                    case 2:
                        return "DML";
                    default:
                        return null;
                }
            }
        },
        {
            title: 'sql内容',
            dataIndex: 'sql_content',
            key: 'sql_content',
            ellipsis: true,
        },
        {
            title: 'sql执行状态',
            key: 'status',
            width: 100,
            render: info => {
                switch (info.status) {
                    case 0:
                        return "执行中";
                    case 1:
                        return "执行成功";
                    case 2:
                        return "执行失败";
                    default:
                        return null;
                }
            }
        },
        {
            title: '操作',
            fixed: 'right',
            width: 80,
            render:info => {
                switch (info.status) {
                    case 2:
                        return <Action>
                            <Action.Button onClick={(e) => store.reloadSqlCont(info)} >重新执行</Action.Button>
                        </Action>;
                }

            }
        }
    ];
    return (
        <Modal
            visible
            width={1000}
            maskClosable={false}
            title="同步测试环境"
            onCancel={() => store.synchronousEnvVisible = false}
            onOk={HandleSubmit}>
            <Form form={form} initialValues={store.synchronousEnvForm}  >
                <Row>
                    <Col span={12}>
                        <Form.Item labelCol={{span: 8}} wrapperCol={{span: 16}} required name="demand_name" label="需求名称" >
                            <Input disabled placeholder="请输入需求名称"/>
                        </Form.Item>
                    </Col>
                    <Col span={12}>
                        <Form.Item labelCol={{span: 6}} wrapperCol={{span: 16}}  required name="demand_link" label="需求链接" >
                            <Input disabled placeholder="请输入需求链接"/>
                        </Form.Item>
                    </Col>
                </Row>

                <Row>
                    <Col span={24}>
                        <Form.Item labelCol={{span: 4}} wrapperCol={{span: 19}}  required name="sync_env" label="已同步测试环境" >
                            <Select
                                mode="multiple"
                                allowClear
                                disabled
                                placeholder="">
                                {store.synchronousEnvList.map( (item,index )    => (
                                    <Select.Option value={item.value} key={index}>{item.label}</Select.Option>
                                ))}
                            </Select>
                        </Form.Item>
                    </Col>
                </Row>
                <Row>
                    <Col span={24}>
                        <Form.Item labelCol={{span: 4}} wrapperCol={{span: 19}}  required name="sync_complete" label="指定同步测试环境" >
                            <Select
                                mode="multiple"
                                allowClear
                                placeholder="请选择指定同步测试环境">
                                {store.synchronousEnvList.map( (item,index )    => (
                                    <Select.Option value={item.value} key={index}>{item.label}</Select.Option>
                                ))}
                            </Select>
                        </Form.Item>
                    </Col>

                </Row>
                <Divider orientation="left">SQL同步记录</Divider>
                <Table
                    columns={tableColumns}
                    dataSource={store.synchronousEnvTableData}
                    bordered
                    size="middle"
                    pagination={false}/>
            </Form>
            {store.reloadSqlVisible &&   <Modal
                visible
                width={500}
                maskClosable={false}
                title="同步测试环境"
                onCancel={() => store.reloadSqlVisible = false}
                onOk={reloadSqlSumbit}>
                <Form form={reloadSqlform} initialValues={store.reloadSqlform} labelCol={{span: 5}} wrapperCol={{span: 17}}>
                    <Row>
                        <Col span={23}>
                            <Form.Item labelCol={{span: 4}} wrapperCol={{span: 20}} required name="sql_content" label="Sql内容" >
                                <TextArea rows={4} />
                            </Form.Item>
                        </Col>

                    </Row>
                </Form>
            </Modal>
            }


        </Modal>

    )
}
export default observer(SynchronousEnv)