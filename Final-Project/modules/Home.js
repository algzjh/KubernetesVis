import React from 'react'
import Namespaces from './Namespaces'


export default React.createClass({
  render() {
    return (
      <div>
        <h3>K8s-Vis</h3>
        <div className="col-md-8">
          <p>Information and Status</p>
          <p>
            use credentials or the config file.
          </p>
        </div>
        <div className="row">
          <div className="col-md-12">
            <Namespaces/>
          </div>
        </div>
      </div>
    )
  }
})
