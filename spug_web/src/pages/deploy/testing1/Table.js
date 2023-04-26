/**
 * Copyright (c) OpenSpug Organization. https://github.com/openspug/spug
 * Copyright (c) <spug.dev@gmail.com>
 * Released under the AGPL-3.0 License.
 */
import React from 'react';
import { observer } from 'mobx-react';
import {  PlusOutlined  } from '@ant-design/icons';
import { Radio,Tag  } from 'antd';
import { hasPermission } from 'libs';
import { Action, AuthButton, TableCard } from 'components';
import S from './index.module.less';
import store from './store';


function DeployConfirm() {
    return (
        <div>
            <div>确认发布方式</div>
            <div style={{color: '#999', fontSize: 12}}>补偿：仅发布上次发布失败的主机。</div>
            <div style={{color: '#999', fontSize: 12}}>全量：再次发布所有主机。</div>
        </div>
    )
}

function ComTable() {
    const columns = [{
        title: '需求名称',
        className: S.min180,
        dataIndex: 'demand_name',
        key: 'demand_name',
    }, {
        title: '开发人员',
        className: S.min180,
        dataIndex: 'developer_name',
        key: 'developer_name',
    }, {
        title: '测试人员',
        className: S.min180,
        dataIndex: 'tester_name',
        key: 'tester_name',
    }, {
        title: 'SQL执行状态',
        className: S.min155,
        key: 'sql_exec_status',
        render: info => {
            switch (info.sql_exec_status) {
                case 0:
                    return <Tag color="green">测试环境待执行</Tag>
                case 1:
                    return <Tag color="green">测试环境执行中</Tag>
                case 2:
                    return <Tag color="green">测试环境已执行</Tag>
                case 3:
                    return <Tag color="green">测试环境执行失败</Tag>
                case 4:
                    return <Tag color="green">线上环境待执行</Tag>
                case 5:
                    return <Tag color="green">线上环境执行中</Tag>
                case 6:
                    return <Tag color="green">线上环境已执行</Tag>
                case 7:
                    return <Tag color="green">线上环境执行失败</Tag>
                default:
                    return null;
            }

        }
    }, {
        title: '工作状态',
        className: S.min120,
        key: 'status',
        render: info => {
            switch (info.status) {
                case 0:
                    return <Tag color="green">待测试</Tag>
                case 1:
                    return <Tag color="green">指定测试</Tag>
                case 2:
                    return <Tag color="green">测试中</Tag>
                case 3:
                    return <Tag color="green">测试完成</Tag>
                case 4:
                    return <Tag color="green">待上线</Tag>
                case 5:
                    return <Tag color="green">上线中</Tag>
                case 6:
                    return <Tag color="green">上线完成</Tag>
                default:
                    return null;
            }

        }
    }, {
        title: '申请时间',
        className: S.min180,
        dataIndex: 'created_at',
        key: 'created_at',
    }, {
        title: '操作',
        fixed: 'right',
        className: hasPermission('deploy.request.do|deploy.request.edit|deploy.request.approve|deploy.request.del') ? S.min180 : 'none',
        render: info => {
            if(info.status == 0){
                return  <Action>
                    <Action.Button onClick={(e) => store.lookDialog(e,info)} >查看</Action.Button>
                    <Action.Button onClick={(e) => store.appointDialog(info,"test")} >指定</Action.Button>
                    <Action.Button onClick={() => store.handleDelete(info)}>删除</Action.Button>
                </Action>
            }else if(info.status == 1){
                return  <Action>
                    <Action.Button onClick={(e) => store.lookDialog(e,info)} >查看</Action.Button>
                    <Action.Button onClick={() => store.handleDelete(info)}>删除</Action.Button>
                </Action>
            }else if(info.status == 2 && (info.sql_exec_status == 0 || info.sql_exec_status == 3 )){
                return  <Action>
                    <Action.Button onClick={(e) => store.lookDialog(e,info)} >查看</Action.Button>
                    <Action.Button onClick={() => store.sqlExecuteWorkOrder(info,"cs")}>SQL测试执行</Action.Button>
                </Action>
            }else if(info.status == 2 && info.sql_exec_status == 2 ){
                return  <Action>
                    <Action.Button onClick={(e) => store.lookDialog(e,info)} >查看</Action.Button>
                    <Action.Button onClick={() => store.testsOk(info,"cs")}>测试完成</Action.Button>
                </Action>
            }else if(info.status == 3 && info.sql_exec_status == 2 ){
                return  <Action>
                    <Action.Button onClick={(e) => store.lookDialog(e,info)} >查看</Action.Button>
                    <Action.Button onClick={(e) => store.retest(e,info)}>重新测试</Action.Button>
                    <Action.Button  onClick={(e) => store.appointDialog(info,"goOnline")}>上线</Action.Button>
                </Action>
            }else if(info.status == 4 && (info.sql_exec_status == 4 || info.sql_exec_status == 7 )){
                return  <Action>
                    <Action.Button onClick={(e) => store.lookDialog(e,info)} >查看</Action.Button>
                    <Action.Button onClick={() => store.sqlExecuteWorkOrder(info,"xs")}>SQL线上执行</Action.Button>
                </Action>
            }else if(info.status == 5 && info.sql_exec_status == 6 ){
                return  <Action>
                    <Action.Button onClick={(e) => store.lookDialog(e,info)} >查看</Action.Button>
                    <Action.Button  onClick={(e) => store.ywgoOnline(e,info)}>运维上线申请</Action.Button>
                </Action>
            }else if(info.status == 6 && info.sql_exec_status == 6 ){
                return  <Action>
                    <Action.Button onClick={(e) => store.lookDialog(e,info)} >查看</Action.Button>
                    <Action.Button onClick={(e) => store.onlineCompletion(e,info)} >上线完成</Action.Button>
                </Action>
            }else if(info.status == 6  ){
                return  <Action>
                    <Action.Button onClick={(e) => store.lookDialog(e,info)} >查看</Action.Button>
                    <Action.Button>同步测试环境</Action.Button>
                </Action>
            }else{
                return  <Action>
                    <Action.Button onClick={(e) => store.lookDialog(e,info)} >查看</Action.Button>

                </Action>
            }
         /*    switch (info.status) {
                default:
                    return <Action>
                        <Action.Button onClick={(e) => store.lookDialog(e,info)} >查看</Action.Button>
                        <Action.Button onClick={(e) => store.appointDialog(info,"test")} >指定</Action.Button>
                        <Action.Button onClick={() => store.handleDelete(info)}>删除</Action.Button>
                        <Action.Button onClick={() => store.sqlExecuteWorkOrder(info)}>SQL执行</Action.Button>
                        <Action.Button onClick={() => store.testsOk(info,"cs")}>测试完成</Action.Button>
                        <Action.Button onClick={(e) => store.retest(e,info)}>重新测试</Action.Button>
                        <Action.Button  onClick={(e) => store.appointDialog(info,"goOnline")}>上线</Action.Button>
                        <Action.Button  onClick={(e) => store.ywgoOnline(e,info)}>运维上线申请</Action.Button>
                        <Action.Button onClick={(e) => store.onlineCompletion(e,info)} >上线完成</Action.Button>
                        <Action.Button onClick={(e) => store.synchronousEnv(info)}>同步测试环境</Action.Button>

                    </Action>;
            }*/
        }
    }];
    return (
        <TableCard
            tKey="dr"
            rowKey={row => row.key || row.id}
            title="申请列表"
            columns={columns}
            scroll={{x: 1500}}
            tableLayout="auto"
            loading={store.isFetching}
            dataSource={store.dataSource}
            onReload={store.fetchRecords}
            actions={[
                <AuthButton
                    auth="deploy.request.add"
                    type="primary"
                    icon={<PlusOutlined/>}
                    onClick={() => store.addDialog()}>新建申请</AuthButton>,
                <Radio.Group value={store.f_status} onChange={e => store.f_status = e.target.value}>
                    <Radio.Button value="all">全部({store.counter['all'] || 0})</Radio.Button>
                    <Radio.Button value="0">待测试({store.counter['0'] || 0})</Radio.Button>
                    <Radio.Button value="1">指定测试({store.counter['1'] || 0})</Radio.Button>
                    <Radio.Button value="2">测试中({store.counter['2'] || 0})</Radio.Button>
                    <Radio.Button value="3">测试完成({store.counter['3'] || 0})</Radio.Button>
                    <Radio.Button value="4">待上线({store.counter['4'] || 0})</Radio.Button>
                    <Radio.Button value="5">上线中({store.counter['5'] || 0})</Radio.Button>
                    <Radio.Button value="6">上线完成({store.counter['6'] || 0})</Radio.Button>
                </Radio.Group>
            ]}
            pagination={{
                showSizeChanger: true,
                showLessItems: true,
                showTotal: total => `共 ${total} 条`,
                pageSizeOptions: ['10', '20', '50', '100']
            }}/>
    )
}

export default observer(ComTable)
