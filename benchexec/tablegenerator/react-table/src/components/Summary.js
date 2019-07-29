import React from 'react';
import ReactTable from 'react-table'
import 'react-table/react-table.css'
import withFixedColumns from 'react-table-hoc-fixed-columns';
import 'react-table-hoc-fixed-columns/lib/styles.css'

const ReactTableFixedColumns = withFixedColumns(ReactTable);

export default class Summary extends React.Component {

    constructor(props) {
        super(props);
        this.state= {
            showTotal: true,
            showLocal: true,
            showCorrect: true,
            showIncorrect: true,
            fixed: true,
        }
        this.infos = ['displayName', 'tool', 'limit', 'host', 'os', 'system', 'date', 'runset', 'branch', 'options', 'property'];
        this.headerWidth = (window.innerWidth*0.15);
        this.width = window.innerWidth;
    };

    renderResultTable = () => {
        return this.props.tools.map((tool, j) => {
            
            return tool.columns.map((column, i) => {
                
                return {
                    id: column.title+j,
                    Header: () => (
                        <div className="columns" title="Show Quantile Plot of this column" onClick={(e) => this.props.changeTab(e, column, 2)}>{column.title + (column.source_unit ? " (" + column.source_unit + ")" : '')}</div>
                        ),
                        show: column.isVisible,
                        accessor: props => (
                        props.content[j][i] ? <div className="summary_span" title={this.renderTooltip(props.content[j][i], j, i)}>{this.prepareStatsValues(props.content[j][i].sum, j, i)}</div> : <div className="summary_span">-</div>
                    ),
                }
            });
        });
    }
    prepareStatsValues = (el, tool, column) => {
        const col = this.props.tools[tool].columns[column];
        if (el) {
            return col.type._max_decimal_digits ? +el.toPrecision(col.type._max_decimal_digits+1) : Math.round(+el);
        } 
    }

    renderTooltip = (cell, j, i) => {
        let string = '';
        Object.keys(cell).forEach(key => { 
            let value = this.prepareStatsValues(cell[key], j, i);
            // if(cell[key] && key!=='sum') (string += `, ${key}: ${cell[key].toFixed(2)}`)
            if(cell[key] && key!=='sum') (string += `, ${key}: ${value}`)
        });
        
        return string.substr(2)
    }
    handleInputChange = (event) => {
        const target = event.target;
        const value = target.checked;
        const name = target.name;
    
        this.setState({
          [name]: value
        });
    }
    renderOptions = (text) => {
        return text.split('-').map(option => {
            return <li key={option}>{option}</li>
        })
    }

    render() {
        const toolColumns = this.renderResultTable();
        const column = [
            {
                Header: () => (
                    <div className="toolsHeader">
                        <form>
                            <label>
                                Fixed:
                            </label>
                            <input name="fixed" type="checkbox" checked={this.state.fixed} onChange={this.handleInputChange} />
                        </form>
                    </div>
                ),
                fixed: this.state.fixed ? 'left' : '',
                width: this.headerWidth,
                columns: [
                    {
                        id: 'summary',
                        width: this.headerWidth,
                        Header: () => (
                            <div
                                onClick={this.props.selectColumn}
                            >
                                <span>Click here to select columns</span>
                            </div>
                        ),
                        accessor: props => (
                            <div dangerouslySetInnerHTML={{ __html: props.title }} title={props.description} className="tr"/>
                        )
                    },
                ]
            },
            ...toolColumns.map((toolColumn, i) => {
                return {   
                    id: 'results',
                    Header: () => (
                        <div className="header__tool-infos">
                            {this.props.getRunSets(this.props.tools[i], i)}
                        </div>  
                    ),
                    columns: toolColumn
                };
            })
        ]

        return (
             <div className = "summary">
                 <h2>Environment</h2>
                <table>
                    <tbody>
                        {this.infos.filter(info => this.props.tableHeader[info] !== null).map((row, i) => {
                            return  <tr key={'tr-'+row}> 
                                        <th key={'td-'+row}>{row}</th>
                                        {this.props.tableHeader[row].content.map((tool, j) => {
                                            return row !=='options' ? <td colSpan={tool[1]} key={tool[0]+j} className='header__tool-row'>{tool[0]} </td> : <td colSpan={tool[1]} key={tool[0]+j} className='header__tool-row options'><ul>{this.renderOptions(tool[0])}</ul></td>})
                                        }
                                    </tr>
                                })}
                    </tbody>
                </table>
                <h2>Summary</h2>
                <ReactTableFixedColumns
                    data={this.props.stats}
                    columns= {column}
                    showPagination={false}
                    className = "-highlight"
                    minRows = {0}
                    sortable = {false}
                    width = {this.width}
                />
                <p>Generated by <a className ="link" href="https://github.com/sosy-lab/benchexec" target="_blank" rel="noopener noreferrer"> BenchExec</a></p>
            </div>
        )
    }
}