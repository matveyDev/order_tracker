import './css/App.css';
import React from "react";
import io from "socket.io-client";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)


class App extends React.Component {
  constructor() {
    super()
    this.serverURL = "http://127.0.0.1:5000/";
    this.socket = io(this.serverURL);
    this.state = {
      columns: [],
      data: [],
      diagramData: {
        labels: [],
        datasets: []
      },
    };
  }

  componentDidMount() {
    this.socket.connect();
    this.socket.on('message', (json) => {
      this.createState(json);
    });
    this.timerId = setInterval(() => {
      this.socket.send('get_data')
    }, 5000);
  };

  componentWillUnmount() {
    this.socket.close();
    clearInterval(this.timerId);
  };

  createState(json) {
    const data = JSON.parse(json);
    const diagramData = this.getDiagramData(data.data);
    this.setState({
      columns: data.columns,
      data: data.data,
      diagramData: diagramData
    });
  };

  getDiagramData(data) {
    let diagramData = {
      labels: [],
      datasets: [{
        data: [],
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
        label: 'Price'
      }]
    };

    for (let index = 0; index < data.length; index++) {
      const values = data[index];
      // Push delivery_expected
      diagramData.labels.push(values[3])
      // Push price
      diagramData.datasets[0].data.push(
        values[2]
      )
    }
    return diagramData;
  };

  getTotal() {
    const data = this.state.data;
    let total = 0;
    for (let index = 0; index < data.length; index++) {
      total += data[index][2];
    }
    return total;
  };

  render() {
    return (
      <div className="App">
        <div className="left-side">
        <Line
            width={1100}
            height={600}
            data={this.state.diagramData}
          />
        </div>
        <div className="right-side">
          <div className="total">
            <div className="total-title">
              <h1>Total</h1>
            </div>
            <div className="total-value">{this.getTotal()}</div>
          </div>
          <div className="table">
            <table>
              <tr>
                {this.state.columns.map((column) => {
                  return <th key={column}>{column}</th>
                })}
              </tr>
              {this.state.data.map((values, index) => {
                return (
                  <tr key={index}>
                    {values.map((value) => <th>{value}</th>)}
                  </tr>
                )
              })}
            </table>
          </div>
        </div>
      </div>
    );
  }
}

export default App;
