import React from 'react';
import { observer } from 'mobx-react';
import {Divider, Table} from "antd";
import store from "./store";
function SQLTable(props) {

    const columns1 = [
        {
            title: 'sql内容',
            dataIndex: 'street1',
            key: 'street1',
        },
        {
            title: '警告信息',
            dataIndex: 'street2',
            key: 'street2',
        },
    ];
    const columns2 = [
        {
            title: 'sql内容',
            dataIndex: 'street1',
            key: 'street1',
        },
        {
            title: '错误信息',
            dataIndex: 'street2',
            key: 'street2',
        },
    ];
/*    store.setSqlTable(props.form);*/
    return (
        <div>
            {store.SqlWarnTable.length>0? <Divider orientation="left">SQL检查 - 警告信息</Divider>:null}
            {store.SqlWarnTable.length>0?
                <Table
                    columns={columns1}
                    dataSource={store.SqlWarnTable}
                    bordered
                    size="middle"
                    pagination={false}
                />:null}
            {store.SqlErrorTable.length>0? <Divider orientation="left">SQL检查 - 错误信息</Divider>:null}
            {store.SqlErrorTable.length>0?
                <Table
                    columns={columns2}
                    dataSource={store.SqlErrorTable}
                    bordered
                    size="middle"
                    pagination={false}
                />:null}
        </div>

    )
}
export default observer(SQLTable)