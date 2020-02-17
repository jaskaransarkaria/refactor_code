import unittest
from baron import parse, dumps

def refactor_for_loop(source_code):
  fst = parse(source_code)
  target = get_target_name(fst)
  if target is None:
    return generate_failure("for loop target out of scope")
  for_loop_target = get_for_loop_target(fst)
  append_arg = get_append_arg(fst)
  iterator_symbol = get_iterator_symbol(fst)
  
  return generate_success(f"""
      {target} = [{append_arg} for {iterator_symbol} in {for_loop_target}]
      """)

def generate_failure(message):
  return {
    "succeeded": False,
    "error_message": message
  }

def get_target_name(fst):
  assignment = [x for x in fst if x['type'] == 'assignment']
  if len(assignment) == 0:
    return None
  return assignment[0]['target']['value']

def get_for_loop(fst):
  return [x for x in fst if x['type'] == 'for'][0]

def get_for_loop_target(fst):
  for_loop = get_for_loop(fst)
  return dumps(for_loop['target'])

def get_append_arg(fst):
  for_loop = get_for_loop(fst)
  atomtrailers = [x for x in for_loop['value'] if x['type'] == 'atomtrailers']
  append_arg = atomtrailers[0]['value'][3]['value']
  return dumps(append_arg)

def get_iterator_symbol(fst):
  for_loop = get_for_loop(fst)
  return dumps(for_loop['iterator'])

def generate_success(refactored_source_code):
  return {
    "succeeded": True,
    "source_code": refactored_source_code
  }

class TestForLoopRefactor (unittest.TestCase):
  def test_replaces_for_loop_with_list_comp(self):
    source_code = """
      result = []
      for i in range (0, 10):
        result.append(i)
      
      print(result)
      """
    actual = refactor_for_loop(source_code)

    expected={
      "succeeded": True,
      "source_code": """
      result = [i for i in range (0, 10)]
      """
}
      
    self.assertEqual(actual, expected)

  def test_cast_to_var(self):
    source_code = """
      acc = []
      for i in range (0, 10):
        acc.append(i)
      """

    expected={
    "succeeded": True,
    "source_code": """
      acc = [i for i in range (0, 10)]
      """
    }
    actual = refactor_for_loop(source_code)

    self.assertEqual(actual, expected)

  def test_iterator_value(self):
    source_code = """
      result = []
      for i in range (0, 10):
        result.append(i*2+5)
      """

    expected={
      "succeeded": True,
      "source_code": """
      result = [i*2+5 for i in range (0, 10)]
      """
    }
    actual = refactor_for_loop(source_code)

    self.assertEqual(actual, expected)
  
  def test_for_loop_target(self):
    source_code = """
        result = []
        for i in [1, 2, 3]:
          result.append(i)      
        """
    fst = parse(source_code)
    actual = refactor_for_loop(source_code)
    expected = {
      "succeeded": True,
      "source_code": """
      result = [i for i in [1, 2, 3]]
      """
    }

    self.assertEqual(actual, expected)
    
  def test_iterator_symbol(self):
    source_code = """
      result = []
      for x in range (0, 10):
        result.append(x)
      """
    expected = {
        "succeeded": True,
        "source_code": """
      result = [x for x in range (0, 10)]
      """
    }
    actual = refactor_for_loop(source_code)

    self.assertEqual(actual, expected)

  def test_accumulator_out_of_scope(self):
    source_code = """
      for x in range (0, 10):
        result.append(x)
      """
    actual = refactor_for_loop(source_code)

    self.assertEquals(actual, {
      "succeeded": False,
      "error_message": "for loop target out of scope"
    })
