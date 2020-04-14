from binance.bind import underline_to_camel

def test_underline_to_camel():
    pairs = [(1234, ''), ('under_form', 'underForm'), ('Under_Form', 'underForm')]
    for input, output in pairs:
        assert underline_to_camel(input) == output



