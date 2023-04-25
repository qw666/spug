import React, { useState, useEffect } from 'react';
import {observer} from "mobx-react";
import store from "./store";
import styles from './index.module.less';
import {Form, Input, Modal , Select, } from "antd";
export default observer(function () {
    const [form] = Form.useForm();
    //表单提交
    function appointHandleSubmit() {
        const formData = form.getFieldsValue();
        console.log(formData);
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