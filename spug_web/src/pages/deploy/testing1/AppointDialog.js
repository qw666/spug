import React, { useState, useEffect } from 'react';
import {observer} from "mobx-react";
import store from "./store";
import http from 'libs/http';
import styles from './index.module.less';
import {Form, Input, message, Modal, Select,} from "antd";
export default observer(function () {
    const [form] = Form.useForm();
    //表单提交
    function appointHandleSubmit() {
        const formData = form.getFieldsValue();
        console.log(formData);
        if(store.appointType === "test"){
            if(formData.tester_name == 0){
                message.error('请指定测试人员');
                return false
            }
            http.patch('/api/gh/workflow/', {
                    id: store.appointForm.id,
                    status: 1,
                    tester_name:formData.tester_name.toString()
                }
            ).then(res => {
                message.success('操作成功');
                store.fetchRecords();
                store.appointVisible = false;
            })
        }
        if(store.appointType === "goOnline"){
            if(formData.notify_name  === undefined){
                message.error('请指定通知人员');
                return false
            }
            http.patch('/api/gh/workflow/', {
                    id: store.appointForm.id,
                    status: store.appointForm.status,
                    notify_name:formData.notify_name.toString()
                }
            ).then(res => {
                message.success('操作成功');
                store.fetchRecords();
                store.appointVisible = false;
            })
        }

    }
    return(
        <Modal
            visible
            width={500}
            maskClosable={false}
            title={store.appointType === "test"?"指定测试人员":"指定通知人员"}
            onCancel={() => store.appointVisible = false}
            onOk={appointHandleSubmit}>
            <Form form={form} initialValues={store.appointForm} labelCol={{span: 5}} wrapperCol={{span: 17}}>
                <Form.Item required name="demand_name" label="需求名称" >
                    <Input disabled  placeholder="请输入需求名称"/>
                </Form.Item>
                {
                    store.appointType === "test" && <Form.Item required name="tester_name" label="测试人员" >
                        <Select
                            mode="multiple"
                            allowClear
                            placeholder="请选择测试人员">
                            {store.testersList.map(item => (
                                <Select.Option value={item.nickname} key={item.nickname}>{item.nickname}</Select.Option>
                            ))}
                        </Select>

                    </Form.Item>
                }
                {
                    store.appointType === "goOnline" && <Form.Item required name="notify_name" label="通知人员" >
                        <Select
                            mode="multiple"
                            allowClear
                            placeholder="请选择通知人员">
                            {store.allList.map(item => (
                                <Select.Option value={item.nickname} key={item.nickname}>{item.nickname}</Select.Option>
                            ))}
                        </Select>

                    </Form.Item>
                }
            </Form>
        </Modal>
    )
})