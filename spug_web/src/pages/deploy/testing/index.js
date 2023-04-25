/**
 * Copyright (c) OpenSpug Organization. https://github.com/openspug/spug
 * Copyright (c) <spug.dev@gmail.com>
 * Released under the AGPL-3.0 License.
 */
import React, { useEffect } from 'react';
import { observer } from 'mobx-react';
import {Select, DatePicker, Input} from 'antd';
import { Breadcrumb,SearchForm } from 'components';
import store from "./store";
import moment from "moment";
import ComTable from './Table';
import AddForm from "./AddForm";
import AppointDialog from './AppointDialog'
import SqlExecuteWorkOrderDialog from "./SqlExecuteWorkOrderDialog";
import TestsComplete from "./TestsComplete";
import SynchronousEnv from "./SynchronousEnv"
export default observer(function () {
    useEffect(() => {
        store.fetchRecords();
        store.getTesterList();
        store.getDevelopersList();
        store.getAllPersonnel();

    }, []);
    return (
        <div>
            <Breadcrumb>
                <Breadcrumb.Item>首页</Breadcrumb.Item>
                <Breadcrumb.Item>应用发布</Breadcrumb.Item>
                <Breadcrumb.Item>提测申请</Breadcrumb.Item>
            </Breadcrumb>
            <SearchForm>

                <SearchForm.Item span={6} title="需求名称">
                    <Input allowClear
                           value={store.demand_name}
                           onChange={e => store.demand_name = e.target.value}
                           placeholder="请输入需求名称"/>
                </SearchForm.Item>
                <SearchForm.Item span={6} title="开发人员">
                    <Select
                              allowClear
                              value={store.developers}
                              onChange={v => store.developers = v}
                              placeholder="请选择">
                        {store.developersList.map(item => (
                            <Select.Option value={item.nickname} key={item.nickname}>{item.nickname}</Select.Option>
                        ))}
                    </Select>
                </SearchForm.Item>
                <SearchForm.Item span={8} title="申请时间">
                    <DatePicker.RangePicker
                        value={store.f_s_date ? [moment(store.f_s_date), moment(store.f_e_date)] : undefined}
                        onChange={store.updateDate}/>
                </SearchForm.Item>
            </SearchForm>
            <ComTable/>
            {store.addVisible && <AddForm/>}
            {store.appointVisible && <AppointDialog/>}
            {store.sqlVisible && <SqlExecuteWorkOrderDialog/>}
            {store.testsCompleteVisible && <TestsComplete/>}
            {store.synchronousEnvVisible && <SynchronousEnv/>}
        </div>

    )
})
