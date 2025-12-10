import React from 'react';

class Form extends React.Component {
  constructor(props, loan_amount, term, percent, total_monthly_installment) {
    super(props);
    this.loan_amount = loan_amount;
    this.term = term;
    this.percent = percent;
    this.total_monthly_installment = total_monthly_installment;

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  // class LoanRequestIn(BaseModel):
  //   user_id: int
  //   loan_amount: float
  //   term: int
  //   percent: float
  //   total_monthly_installment: float

  handleChange(event) {
    this.setState({value: event.target.loan_amount});
    this.setState({value: event.target.term});
    this.setState({value: event.target.percent});
    this.setState({value: event.target.total_monthly_installment});
  }

  handleSubmit(event) {
    alert('Žadost jsem přijal');
    event.preventDefault();
  }

  render() {
    return (
      <form onSubmit={this.handleSubmit}>
        <label>
          Amount:
          <input type="text" value={this.state.loan_amount} onChange={this.handleChange} />
        </label>
        <label>
          Term of loan:
          <input type="text" value={this.state.term} onChange={this.handleChange} />
        </label>
        <label>
          Percent:
          <input type="text" value={this.state.percent} onChange={this.handleChange} />
        </label>
        <label>
          Monthly installment:
          <input type="text" value={this.state.total_monthly_installment} onChange={this.handleChange} />
        </label>
        <input type="submit" value="Poslat žadost" />
      </form>
    );
  }
}

export default Form;