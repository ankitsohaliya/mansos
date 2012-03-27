# -*- coding: utf-8 -*-
#
# Copyright (c) 2008-2012 the MansOS team. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#  * Redistributions of source code must retain the above copyright notice,
#    this list of  conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#'

import time
import ply.lex as lex
import ply.yacc as yacc

from parameter import Parameter
from statement import Statement
from condition_container import ConditionContainer
from condition import Condition
from comment import Comment

class SealParser():
    def __init__(self, printMsg):

        self.commentQueue = Comment()
        self.commentStack = []
        self.printMsg = printMsg

        self.lex = lex.lex(module = self, debug = True)

        self.yacc = yacc.yacc(module = self, debug = True)

        print "Lex & Yacc init done!"
        print "Remember! Cache is used, so warnings are showed only at first compilation!"

    def run(self, s, silent = False):
        self.result = []
        self.silent = silent
        if s != None:
            self.currLine = 1
            start = time.time()
            # \n added because needed! helps resolving conflicts
            self.yacc.parse('\n' + s + '\n')
            if not self.silent:
                print "Parsing done in %.4f s" % (time.time() - start)

        #=======================================================================
        # for x in self.result:
        #    print x
        #    if x != None:
        #        print x.getCode("") + '\n'
        #=======================================================================
        return self.result

### Lex

    # Tokens
    reserved = {
      "use": "USE_TOKEN",
      "read": "READ_TOKEN",
      "sendto": "SENDTO_TOKEN",
      "when": "WHEN_TOKEN",
      "else": "ELSE_TOKEN",
      "elsewhen": "ELSEWHEN_TOKEN",
      "end": "END_TOKEN",
      "code": "CODE_TOKEN",
      "true": "TRUE_TOKEN",
      "false": "FALSE_TOKEN",
      "not": "NOT_TOKEN",
      "==": "EQ_TOKEN",
      "!=": "NEQ_TOKEN",
      ">": "GR_TOKEN",
      "<": "LE_TOKEN",
      ">=": "GEQ_TOKEN",
      "<=": "LEQ_TOKEN",
      ">": "GR_TOKEN",
      }

    t_CODE_BLOCK = r'\"\"\".*\"\"\"'

    tokens = [
        'CODE_BLOCK', 'IDENTIFIER_TOKEN', 'SECONDS_TOKEN',
        'MILISECONDS_TOKEN', 'INTEGER_TOKEN', 'COMMENT_TOKEN' #, 'newline'
        ] + list(reserved.values())

    literals = ['.', ',', ':', ';', '{', '}']

    def t_IDENTIFIER_TOKEN(self, t):
        r'[a-zA-Z_][0-9a-zA-Z_]*'
        # This checks if no reserved token is met!!
        t.type = self.reserved.get(t.value, "IDENTIFIER_TOKEN")
        return t

    def t_SECONDS_TOKEN(self, t):
        r'[0-9]+s'
        return t

    def t_MILISECONDS_TOKEN(self, t):
        r'[0-9]+ms'
        #t.value = int(t.value[:-2])
        return t

    def t_INTEGER_TOKEN(self, t):
        r'[0-9]+'
        t.value = int(t.value)
        return t

    def t_COMMENT_TOKEN(self, t):
        r'''//.*'''
        t.value = t.value.strip("/ ")
        print 'comment:', t.value
        return t

    # Needed for OP :)
    def t_HELP_TOKEN(self, t):
        r'[=<>!][=]?'
        # This checks if no reserved token is met!!
        t.type = self.reserved.get(t.value, "HELP_TOKEN")
        return t

    t_ignore = " \t\r\n"

#    def t_newline(self, t):
#        r'\n'
#        print "newline", t.lexer.lineno
#        t.lexer.lineno += t.value.count("\n")
#        self.currLine += 1
#        return t

    def t_error(self, t):
        if not self.silent:
            self.printMsg("Line '%d': Illegal character '%s'" %
                      (self.currLine, t.value[0]))
        t.lexer.skip(1)

### YACC

    def p_program(self, p):
        '''program : declaration_list
        '''
        self.result = p[1]

    def p_declaration_list(self, p):
        '''declaration_list : declaration_list declaration
                            |
        '''
        if len(p) == 1:
            p[0] = []
        elif len(p) == 3:
            if p[2] != None:
                p[1].append(p[2])
            p[0] = p[1]

    def p_USE_TOKEN_C(self, p):
        '''USE_TOKEN_C : USE_TOKEN
                         | USE_TOKEN COMMENT_TOKEN '''
        p[0] = p[1]

    def p_READ_TOKEN_C(self, p):
        '''READ_TOKEN_C : READ_TOKEN
                          | READ_TOKEN COMMENT_TOKEN '''
        p[0] = p[1]

    def p_SENDTO_TOKEN_C(self, p):
        '''SENDTO_TOKEN_C : SENDTO_TOKEN
                            | SENDTO_TOKEN COMMENT_TOKEN '''
        p[0] = p[1]

    def p_declaration(self, p):
        '''declaration : USE_TOKEN_C IDENTIFIER_TOKEN parameter_list ';'
                       | READ_TOKEN_C IDENTIFIER_TOKEN parameter_list ';'
                       | SENDTO_TOKEN_C IDENTIFIER_TOKEN packet_field_specifier parameter_list ';'
                       | when_block
                       | code_block
                       | COMMENT_TOKEN
        '''
        if len(p) == 2:
            # code_block, when_block
            if not isinstance(p[1], str):
                p[0] = p[1]
            #comment_list
            else:
                self.commentStack.append(p[1])
        else:
            p[0] = Statement(p[1], p[2])
            # use & read
#            if len(p) == 6:
#                self.queueComment(p[5])
#                p[0].setParameters(p[3])
#            # send_to
#            elif len(p) == 7:
#                self.queueComment(p[6])
#                p[0].setParameters(p[4])
                # TODO: parse packet_field
            if p[1] == 'use' or p[1] == 'read':
#                self.queueComment(p[2])
                p[0].setParameters(p[3])
            else: # sendto
#                self.queueComment(p[2])
#                self.queueComment(p[4])
                p[0].setParameters(p[4])
#            self.queueComment(self.commentStack.pop(), True)
            p[0].setComment(self.getQueuedComment())

    def p_when_block(self, p):
        '''when_block : WHEN_TOKEN condition ":" declaration_list elsewhen_block END_TOKEN
        '''
        p[0] = p[5]
        newCond = Condition("when")
        newCond.setCondition(p[2])
        newCond.setStatements(p[4])
#        self.queueComment(p[4])
#        if len(self.commentStack) > 1:
#            self.queueComment(self.commentStack.pop(-2), True)
#        newCond.setComment(self.getQueuedComment())

#        self.queueComment(p[2])
#        self.queueComment(p[4])
        #self.queueComment(self.commentStack.pop(), True)
        #p[0].setEndComment(self.getQueuedComment())
        p[0].setWhen(newCond)
        # Needed because elsewhen's arrive in reverse order
        p[0].fixElseWhenOrder()

    def p_elsewhen_block(self, p):
        '''elsewhen_block : ELSEWHEN_TOKEN condition ":" declaration_list elsewhen_block
                          | ELSE_TOKEN ":" declaration_list
                          | 
        '''
        p[0] = ConditionContainer()
        # else
        if len(p) == 4:
            newCond = Condition("else")
            newCond.setStatements(p[3])
#            self.queueComment(p[3])
#            if len(self.commentStack) > 1:
#                self.queueComment(self.commentStack.pop(-2), True)
            newCond.setComment(self.getQueuedComment())
            p[0].setElse(newCond)
        # elsewhen
        elif len(p) == 6:
            p[0] = p[5]
            newCond = Condition("elsewhen")
            newCond.setCondition(p[2])
            newCond.setStatements(p[4])
#            self.queueComment(p[4])
#            self.queueComment(self.commentStack.pop(), True)
#            newCond.setComment(self.getQueuedComment())
            p[0].addElseWhen(newCond)

    def p_code_block(self, p):
        '''code_block : CODE_TOKEN IDENTIFIER_TOKEN CODE_BLOCK
        '''
        # ???

    def p_packet_field_specifier(self, p):
        '''packet_field_specifier : "{" packet_field_list "}"
        '''

    def p_packet_field_list(self, p):
        '''packet_field_list : packet_field_list "," packet_field
                             | packet_field
        '''

    def p_packet_field(self, p):
        '''packet_field : IDENTIFIER_TOKEN
                        | IDENTIFIER_TOKEN value
        '''

    # Comments at end of line AFTER code, doesn't include newline on purpose.
#    def p_comment(self, p):
#        '''comment : COMMENT_TOKEN
#                   |
#        '''
#        if len(p) == 2:
#            p[0] = p[1]
#        else:
#            p[0] = ''

    # comment_list is the only token who accepts newlines, that means that at
    # each line there is one comment_list, it may be empty, but this assumption 
    # allows comment stack to work properly and grammar to be conflict free.
    # Conflict rises when declaration_list and comment_list both can be empty! 
    # This is reason why code must start and end with newline.
#    def p_comment_list(self, p):
#        '''comment_list : comment_list COMMENT_TOKEN newline
#                        | newline
#        '''
#        # True added so this can be recognized later as tuple
#        if len(p) == 2:
#            p[0] = []
#        elif len(p) == 4:
#            p[1].append(p[2])
#            p[0] = p[1]

#    def p_comment_list(self, p):
#        '''comment_list : comment_list COMMENT_TOKEN
#                        |
#        '''
#        if len(p) == 2:
#            # so this can be recognized later as tuple
#            p[0] = []
#        else:
#            p[1].append(p[2])
#            p[0] = p[1]

    def p_comment_list(self, p):
        '''comment_list : comment_list COMMENT_TOKEN
                        | COMMENT_TOKEN
        '''
        pass # TODO

    def p_COMMA_C(self, p):
        '''COMMA_C : ',' comment_list
                     | ','
        '''
        pass


    def p_parameter_list(self, p):
        '''parameter_list : parameter_list COMMA_C parameter
                          |'''
        if len(p) == 1:
            p[0] = []
        elif len(p) == 4:
            p[1].append(p[3])
            p[0] = p[1]

    def p_parameter(self, p):
        '''parameter : IDENTIFIER_TOKEN
                     | IDENTIFIER_TOKEN value
                     | WHEN_TOKEN condition
        '''
        if len(p) == 2:
            p[0] = Parameter(p[1], True)
        # Works for both cases, in condition case parameter's name is when :)
        # Idea is that if when exist will always be last parameter, but
        # maybe we can allow it to be any parameter.
        elif len(p) == 3:
            p[0] = Parameter(p[1], p[2])

    def p_value(self, p):
        '''value : boolean_value
                 | qualified_number
                 | IDENTIFIER_TOKEN
        '''
        p[0] = p[1]

    def p_boolean_value(self, p):
        '''boolean_value : TRUE_TOKEN
                         | FALSE_TOKEN
        '''
        p[0] = p[1]

    def p_qualified_number(self, p):
        '''qualified_number : INTEGER_TOKEN
                            | SECONDS_TOKEN
                            | MILISECONDS_TOKEN
        '''
        p[0] = p[1]

    def p_condition(self, p):
        '''condition : class_parameter
                     | NOT_TOKEN class_parameter
                     | class_parameter op qualified_number
                     | qualified_number op class_parameter
                     | NOT_TOKEN class_parameter op qualified_number
                     | NOT_TOKEN qualified_number op class_parameter
                     | boolean_value
        '''
        p[0] = p[1]
        for x in range(2, len(p)):
            p[0] += ' ' + p[x]

    def p_class_parameter(self, p):
        '''class_parameter : IDENTIFIER_TOKEN "." IDENTIFIER_TOKEN
        '''
        p[0] = p[1] + "." + p[3]

    def p_op(self, p):
        ''' op : EQ_TOKEN
               | NEQ_TOKEN
               | GR_TOKEN
               | LE_TOKEN
               | GEQ_TOKEN
               | LEQ_TOKEN
        '''
        p[0] = p[1]

    def p_error(self, p):
        if not self.silent:
            if p:
                self.printMsg("Line '%d': Syntax error at '%s'" % (self.currLine, p.value))
            else:
                self.printMsg("Line '%d': Syntax error at EOF" % self.currLine)

### Helpers

    def queueComment(self, comment, pre = False):
        if pre:
            if isinstance(comment, list):
                for x in comment:
                    self.commentQueue.addPreComment(x)
            else:
                self.commentQueue.setPreComments(comment)
        else:
            self.commentQueue.setPostComment(comment)

    def getQueuedComment(self):
        queuedComment = self.commentQueue
        self.commentQueue = Comment([], '')
        return queuedComment
