import React, { useState, useEffect } from 'react';
import {observer} from "mobx-react";
import store from "./store";
import http from 'libs/http';
import styles from './index.module.less';
import {Form, Input, Modal, Select, Space, Upload,message,Button} from "antd";
import {UploadOutlined} from "@ant-design/icons";
import { X_TOKEN } from 'libs';
export default observer(function () {
    const [par, setPar] = useState({
        test_case :"",
        test_report:"",
    });
    const [uploadType, setUploadType] = useState({});
    const [form] = Form.useForm();
    //表单提交
    function appointHandleSubmit() {
        const formData = form.getFieldsValue();
        http.patch('/api/gh/test/', {
            id: store.testsCompleteForm.id,
            test_case:par.test_case,
            test_report:par.test_report,
        }).then(res => {
            message.success('操作成功');
            store.fetchRecords();
            store.testsCompleteVisible = false;
        })
    }
    function handleUploadChange(info) {
        console.log(info.file.status);
    }
    function handleUpload1(file, fileList) {
        let isTrue = "";
        let FileExt = file.name.replace(/.+\./, "");
        //验证图片格式
        if (["xls", "xlsx","docx"].indexOf(FileExt.toLowerCase()) === -1) {
            isTrue = false;
        } else {
            isTrue = true;
        }

        if (!isTrue) {
            message.error("只能上传xls、xlsx格式的文件");
            return
        }

        const formData = new FormData();
        formData.append('file', file);

        console.log(" console.log(files);",formData);
        http.post('/api/gh/minio/fileupload/', formData).then((res) => {
            if(uploadType === "test_case"){
                setPar({
                    ...par,
                    test_case:res
                })
            }
            if(uploadType === "test_report"){
                setPar({
                    ...par,
                    test_report:res
                })
            }
            message.success('保存成功');
         })
    }
    function handleUpload2(file, fileList) {

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
                        action={"/api/gh/minio/fileupload/"}
                        beforeUpload={handleUpload1}
                        headers={{'X-Token': X_TOKEN}}
                        maxCount={1}
                        onChange={handleUploadChange}
                    >
                        <Space className="btn">
                        <Button onClick={ () => {
                            setUploadType("test_report")
                        }}><UploadOutlined/>上传测试报告</Button>
                        </Space>
                    </Upload>
                </Form.Item>
                <Form.Item required name="name3" label="测试用例" >
                    <Upload
                        maxCount={1}
                        action={"/api/gh/minio/fileupload/"}
                        beforeUpload={handleUpload1}
                        headers={{'X-Token': X_TOKEN}}
                    >
                        <Space className="btn">
                            <Button onClick={()=>{
                                setUploadType("test_case")
                            }}><UploadOutlined/>上传测试用例</Button></Space>
                    </Upload>
                </Form.Item>
            </Form>
        </Modal>
    )
})