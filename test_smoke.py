import sys, unittest
sys.path.insert(0,'.')
from hello_tool import query_tool,TOOLS
class Smoke(unittest.TestCase):
 def test_six_tools(self):self.assertGreaterEqual(len(TOOLS),6)
 def test_leave(self):
  d=query_tool('search_rules','病假要怎麼請假？');self.assertTrue(any('請假' in e['title'] for e in d['evidence']))
 def test_contacts(self):self.assertIn('evidence',query_tool('search_contacts','教務主任分機'))
 def test_calendar(self):self.assertIn('evidence',query_tool('search_calendar','9月6日校務行事曆'))
 def test_announcements_not_invented(self):
  d=query_tool('search_announcements','明天校外教學取消嗎');self.assertEqual(d['evidence'],[]);self.assertIn('未接入',d['note'])
 def test_no_fake_document_url(self):
  for e in query_tool('search_rules','病假')['evidence']:self.assertIsNone(e['url'])
if __name__=='__main__':unittest.main()
