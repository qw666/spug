import React, { useState, useEffect } from 'react';
import {observer} from "mobx-react";
import store from "./store";
import styles from './index.module.less';
import {Form, Input, Modal, Select, Space, Upload,message} from "antd";
import {UploadOutlined} from "@ant-design/icons";
export default observer(function () {
    const [files, setFiles] = useState([]);

    const [form] = Form.useForm();
    //表单提交
    function appointHandleSubmit() {
        const formData = form.getFieldsValue();
        console.log(formData);
    }
    function handleUpload(file, fileList) {
        console.log(file);
        let isTrue = "";
        let FileExt = file.name.replace(/.+\./, "");
        //验证图片格式
       /* if (["xls", "xlsx"].indexOf(FileExt.toLowerCase()) === -1) {
            isTrue = false;
        } else {
            isTrue = true;
        }

        if (!isTrue) {
            message.error("只能上传xls、xlsx格式的文件");
            return
        }*/

        const tmp = files.length > 0 && files[0].type === 'upload' ? [...files] : []
        for (let file of fileList) {
            tmp.push({ type: 'upload', name: '本地上传', path: file})
        }
        setFiles(tmp);
        return Upload.LIST_IGNORE
    }
    return(
        <Modal
            visible
            width={500}
            maskClosable={false}
            title="测试完成"
            onCancel={() => store.testsCompleteVisible = false}
            onOk={appointHandleSubmit}>
            <Form form={form} initialValues={store.testsCompleteForm} labelCol={{span: 5}} wrapperCol={{span: 17}}>
                <Form.Item required name="demand_name" label="需求名称" >
                    <Input  disabled  placeholder="请输入需求名称"/>
                </Form.Item>
                <Form.Item  required name="developer_name" label="开发人员" >
                    <Select
                        mode="multiple"
                        allowClear
                        disabled
                        placeholder="请选择">
                        {store.developersList.map( (item,index )    => (
                            <Select.Option value={item.nickname} key={index}>{item.nickname}</Select.Option>
                        ))}
                    </Select>
                </Form.Item>
                <Form.Item required name="tester_name" label="测试人员" >
                    <Select
                        mode="multiple"
                        allowClear
                        disabled
                        placeholder="请选择">
                        {store.testersList.map(item => (
                            <Select.Option value={item.nickname} key={item.nickname}>{item.nickname}</Select.Option>
                        ))}
                    </Select>
                </Form.Item>
                <Form.Item required name="name3" label="测试报告" >
                    <Upload
                        beforeUpload={handleUpload} maxCount={1}>
                        <Space className="btn"><UploadOutlined/>上传测试报告</Space>
                    </Upload>
                </Form.Item>
                <Form.Item required name="name3" label="测试用例" >
                    <Upload
                        beforeUpload={handleUpload} maxCount={1}>
                        <Space className="btn"><UploadOutlined/>上传测试用例</Space>
                    </Upload>
                </Form.Item>
            </Form>
        </Modal>
    )
})