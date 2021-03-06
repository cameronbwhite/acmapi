"""
"""
import unittest

import json

import datetime

from freezegun import freeze_time

from flask import Flask

from flask.ext.restful import fields, marshal
from flask.ext.restful.fields import MarshallingException

from acmapi.fields import Date
from acmapi.fields import root_fields
from acmapi.fields import event_fields
from acmapi.fields import post_fields
from acmapi.fields import person_fields
from acmapi.fields import membership_fields
from acmapi.fields import officership_fields

import acmapi

from acmapi import models
from acmapi import resources
from acmapi import DB

from acmapi.resources import API
from acmapi.models import Person
from acmapi.models import Officership

import  base64

HEADERS={
     'Authorization': 'Basic ' + base64.b64encode("root:1234")
     }

class test_people_resource(unittest.TestCase):


    @freeze_time("2012-01-14 12:00:01")
    def setUp(self):

        self.maxDiff = None

        self.app = acmapi.create_app(SQLALCHEMY_DATABASE_URI='sqlite://')
        self.app.testing = True
        
        with self.app.test_request_context():
            DB.create_all()
            person = Person.create(
                name = None,
                username = 'root',
                email = None,
                website = None,
                password = '1234',
            )
            DB.session.add(person)
            DB.session.commit()

            officership = Officership.create(
                person = person,
                title = 'Vice Chair',        
                start_date = datetime.date.today(),
                end_date = None,
            )

            DB.session.add(person)
            DB.session.add(officership)
            DB.session.commit()

    @freeze_time("2012-01-14 12:00:01")
    def test_add_unique_person(self):
        
        with self.app.test_client() as client:
            response = client.post(
                'http://localhost:5000/people/',
                headers = HEADERS,
                data = {
                    'username': 'bob',
                    'name': 'Bob Billy',
                    'email': 'bbob@example.com',
                    'website': 'http://bbob.example.com',
                    'password': 'password1234',
                })
        
            self.assertEqual(
                json.loads(response.data),
                {
                    'id': 2,
                    'username': 'bob',
                    'name': 'Bob Billy',
                    'email': 'bbob@example.com',
                    'website': 'http://bbob.example.com',
                    'gravatar_email': None,
                    'gravatar_id': None,
                    'avatar_url': None,
                })

    @freeze_time("2012-01-14 12:00:01")
    def test_add_duplicate_person(self):
        
        with self.app.test_client() as client:
            response = client.post(
                'http://localhost:5000/people/',
                headers = HEADERS,
                data  = {
                    'username': 'bob',
                    'name': 'Bob Billy',
                    'email': 'bbob@example.com',
                    'website': 'http://bbob.example.com',
                    'password': 'password1234',
                })
        
            response = client.post(
                'http://localhost:5000/people/',
                headers = HEADERS,
                data  = {
                    'username': 'bob',
                    'name': 'Bob Billy',
                    'email': 'bbob@example.com',
                    'website': 'http://bbob.example.com',
                    'password': 'password1234',
                })
        
            self.assertEqual(
                json.loads(response.data),
                {
                    'message': 'username already exists'
                })

    @freeze_time("2012-01-14 12:00:01")
    def test_find_existing_person_by_id(self):
        
        with self.app.test_client() as client:
            response = client.post(
                'http://localhost:5000/people/',
                headers = HEADERS,
                data  = {
                    'username': 'bob',
                    'name': 'Bob Billy',
                    'email': 'bbob@example.com',
                    'website': 'http://bbob.example.com',
                    'password': 'password1234',
                })
            
            response = client.get(
                    'http://localhost:5000/people/2')
        
            self.assertEqual(
                json.loads(response.data),
                {
                    'id': 2,
                    'username': 'bob',
                    'name': 'Bob Billy',
                    'email': 'bbob@example.com',
                    'website': 'http://bbob.example.com',
                    'gravatar_email': None,
                    'gravatar_id': None,
                    'avatar_url': None,
                })

    @freeze_time("2012-01-14 12:00:01")
    def test_find_existing_person_by_username(self):
        
        with self.app.test_client() as client:
            response = client.post(
                'http://localhost:5000/people/',
                headers = HEADERS,
                data  = {
                    'username': 'bob',
                    'name': 'Bob Billy',
                    'email': 'bbob@example.com',
                    'website': 'http://bbob.example.com',
                    'password': 'password1234',
                })
            
            response = client.get(
                    'http://localhost:5000/people/bob')
        
            self.assertEqual(
                json.loads(response.data),
                {
                    'id': 2,
                    'username': 'bob',
                    'name': 'Bob Billy',
                    'email': 'bbob@example.com',
                    'website': 'http://bbob.example.com',
                    'gravatar_email': None,
                    'gravatar_id': None,
                    'avatar_url': None,
                })

    @freeze_time("2012-01-14 12:00:01")
    def test_find_non_existing_person_by_id(self):
        
        with self.app.test_client() as client:
            
            response = client.get(
                    'http://localhost:5000/people/2')
        
            self.assertEqual(
                json.loads(response.data),
                {
                    'exception': 'LookupError',
                    'message': 'person not found',
                })

    @freeze_time("2012-01-14 12:00:01")
    def test_find_non_existing_person_by_username(self):
        
        with self.app.test_client() as client:
            
            response = client.get(
                    'http://localhost:5000/people/bob')
        
            self.assertEqual(
                json.loads(response.data),
                {
                    'exception': 'LookupError',
                    'message': 'person not found',
                })

    @freeze_time("2012-01-14 12:00:01")
    def test_list_everything_0(self):
        with self.app.test_client() as client:
            
            response = client.get(
                    'http://localhost:5000/people/')
        
            self.assertEqual(
                json.loads(response.data),
                {
                    'page': 1,
                    'pagesize': 10,
                    'nextpage': None,
                    'people': [
                        { 'id': 1,
                            'username': 'root',
                            'name': None,
                            'email': None,
                            'website': None,
                            'gravatar_email': None,
                            'gravatar_id': None,
                            'avatar_url': None,
                         }
                    ]
                })

    @freeze_time("2012-01-14 12:00:01")
    def test_list_everything_1(self):
        with self.app.test_client() as client:
            
            response = client.post(
                'http://localhost:5000/people/',
                headers = HEADERS,
                data  = {
                    'username': 'bob',
                    'name': 'Bob Billy',
                    'email': 'bbob@example.com',
                    'website': 'http://bbob.example.com',
                    'password': 'password1234',
                })

            response = client.get(
                    'http://localhost:5000/people/')
        
            self.assertEqual(
                json.loads(response.data),
                {
                    'page': 1,
                    'pagesize': 10,
                    'nextpage': None,
                    'people': [
                        {
                            'id': 1,
                            'username': 'root',
                            'name': None,
                            'email': None,
                            'website': None,
                            'gravatar_email': None,
                            'gravatar_id': None,
                            'avatar_url': None,
                            },
                            {
                            'id': 2,
                            'username': 'bob',
                            'name': 'Bob Billy',
                            'email': 'bbob@example.com',
                            'website': 'http://bbob.example.com',
                            'gravatar_email': None,
                            'gravatar_id': None,
                            'avatar_url': None,
                        }
                    ]
                })

    @freeze_time("2012-01-14 12:00:01")
    def test_list_everything_2(self):
        with self.app.test_client() as client:
            
            response = client.post(
                'http://localhost:5000/people/',
                headers = HEADERS,
                data  = {
                    'username': 'bob',
                    'name': 'Bob Billy',
                    'email': 'bbob@example.com',
                    'website': 'http://bbob.example.com',
                    'password': 'password1234',
                })

            response = client.post(
                'http://localhost:5000/people/',
                headers = HEADERS,
                data  = {
                    'username': 'foo',
                    'name': 'Foo Bar',
                    'email': 'foobar@example.com',
                    'website': 'http://foobar.example.com',
                    'password': 'password1234',
                })

            response = client.get(
                    'http://localhost:5000/people/')
        
            self.assertEqual(
                json.loads(response.data),
                {
                    'page': 1,
                    'pagesize': 10,
                    'nextpage': None,
                    'people': [
                        {
                            'id': 1,
                            'username': 'root',
                            'name': None,
                            'email': None,
                            'website': None,
                            'gravatar_email': None,
                            'gravatar_id': None,
                            'avatar_url': None,
                            },
                        {
                            'id': 2,
                            'username': 'bob',
                            'name': 'Bob Billy',
                            'email': 'bbob@example.com',
                            'website': 'http://bbob.example.com',
                            'gravatar_email': None,
                            'gravatar_id': None,
                            'avatar_url': None,
                        },
                        {
                            'id': 3,
                            'username': 'foo',
                            'name': 'Foo Bar',
                            'email': 'foobar@example.com',
                            'website': 'http://foobar.example.com',
                            'gravatar_email': None,
                            'gravatar_id': None,
                            'avatar_url': None,
                        }
                    ]
                })

    @freeze_time("2012-01-14 12:00:01")
    def test_delete_existing_by_id(self):
        with self.app.test_client() as client:
            
            response = client.post(
                'http://localhost:5000/people/',
                headers = HEADERS,
                data  = {
                    'username': 'bob',
                    'name': 'Bob Billy',
                    'email': 'bbob@example.com',
                    'website': 'http://bbob.example.com',
                    'password': 'password1234',
                })

            response = client.delete(
                    'http://localhost:5000/people/2',
                    headers = HEADERS)

            self.assertEqual(
                json.loads(response.data),
                { 'message': 'delete successful' })

            response = client.get(
                    'http://localhost:5000/people/')
             
            self.assertEqual(
                json.loads(response.data),
                {
                    'page': 1,
                    'pagesize': 10,
                    'nextpage': None,
                    'people': [
                        { 'id': 1,
                          'username': 'root',
                          'name': None,
                          'email': None,
                          'website': None,
                          'gravatar_email': None,
                          'gravatar_id': None,
                          'avatar_url': None,
                        }
                    ]
                })

    @freeze_time("2012-01-14 12:00:01")
    def test_delete_existing_by_username(self):
        with self.app.test_client() as client:
            
            response = client.post(
                'http://localhost:5000/people/',
                headers = HEADERS,
                data  = {
                    'username': 'bob',
                    'name': 'Bob Billy',
                    'email': 'bbob@example.com',
                    'website': 'http://bbob.example.com',
                    'password': 'password1234',
                })

            response = client.delete(
                    'http://localhost:5000/people/bob',
                    headers = HEADERS)

            self.assertEqual(
                json.loads(response.data),
                { 'message': 'delete successful' })

            response = client.get(
                    'http://localhost:5000/people/')
             
            self.assertEqual(
                json.loads(response.data),
                {
                    'page': 1,
                    'pagesize': 10,
                    'nextpage': None,
                    'people': [
                        { 'id': 1,
                          'username': 'root',
                          'name': None,
                          'email': None,
                          'website': None,
                          'gravatar_email': None,
                          'gravatar_id': None,
                          'avatar_url': None,
                        }
                    ]
                })

    @freeze_time("2012-01-14 12:00:01")
    def test_delete_non_existing_by_id(self):
        with self.app.test_client() as client:
            
            response = client.delete(
                    'http://localhost:5000/people/2',
                    headers = HEADERS)

            self.assertEqual(
                json.loads(response.data),
                { 'exception': 'LookupError',
                  'message': 'person not found' })

            response = client.get(
                    'http://localhost:5000/people/')
             
            self.assertEqual(
                json.loads(response.data),
                {
                    'page': 1,
                    'pagesize': 10,
                    'nextpage': None,
                    'people': [
                        { 'id': 1,
                          'username': 'root',
                          'name': None,
                          'email': None,
                          'website': None,
                          'gravatar_email': None,
                          'gravatar_id': None,
                          'avatar_url': None,
                        }
                    ]
                })

    @freeze_time("2012-01-14 12:00:01")
    def test_delete_non_existing_by_username(self):
        with self.app.test_client() as client:
            
            response = client.delete(
                    'http://localhost:5000/people/bob',
                    headers = HEADERS)

            self.assertEqual(
                json.loads(response.data),
                { 'exception': 'LookupError',
                  'message': 'person not found' })

            response = client.get(
                    'http://localhost:5000/people/')
             
            self.assertEqual(
                json.loads(response.data),
                {
                    'page': 1,
                    'pagesize': 10,
                    'nextpage': None,
                    'people': [
                        { 
                            'id': 1,
                            'username': 'root',
                            'name': None,
                            'email': None,
                            'website': None,
                            'gravatar_email': None,
                            'gravatar_id': None,
                            'avatar_url': None,
                        }
                    ]
                })

    @freeze_time("2012-01-14 12:00:01")
    def test_invalid_delete(self):
        with self.app.test_client() as client:
            
            response = client.delete(
                    'http://localhost:5000/people/',
                    headers = HEADERS)

            self.assertEqual(
                json.loads(response.data),
                {u'exception': u'LookupError', u'message': u'person not found'}) 
            response = client.get(
                    'http://localhost:5000/people/')
             
            self.assertEqual(
                json.loads(response.data),
                {
                    'page': 1,
                    'pagesize': 10,
                    'nextpage': None,
                    'people': [
                        { 
                            'id': 1,
                            'username': 'root',
                            'name': None,
                            'email': None,
                            'website': None,
                            'gravatar_email': None,
                            'gravatar_id': None,
                            'avatar_url': None,
                        }
                    ]
                })

    @freeze_time("2012-01-14 12:00:01")
    def test_update_existing_person_by_id(self):
        with self.app.test_client() as client:

            response = client.post(
                'http://localhost:5000/people/',
                headers = HEADERS,
                data  = {
                    'username': 'bob',
                    'name': 'Bob Billy',
                    'email': 'bbob@example.com',
                    'website': 'http://bbob.example.com',
                    'password': 'password1234',
                })

            response = client.put(
                'http://localhost:5000/people/2',
                headers = HEADERS,
                data  = {
                    'username': 'bob',
                    'name': 'Jim Billy',
                    'email': 'jbob@example.com',
                    'website': 'http://jbob.example.com',
                })
        
            self.assertEqual(
                json.loads(response.data),
                {'email': 'jbob@example.com',
                 'id': 2,
                 'name': 'Jim Billy',
                 'username': 'bob',
                 'website': 'http://jbob.example.com',
                 'gravatar_email': None,
                 'gravatar_id': None,
                 'avatar_url': None,
                 })


            response = client.get(
                'http://localhost:5000/people/2')

            self.assertEqual(
                json.loads(response.data),
                {
                    'id': 2,
                    'username': 'bob',
                    'name': 'Jim Billy',
                    'email': 'jbob@example.com',
                    'website': 'http://jbob.example.com',
                    'gravatar_email': None,
                    'gravatar_id': None,
                    'avatar_url': None,
                })

    @freeze_time("2012-01-14 12:00:01")
    def test_update_existing_person_by_username(self):
        with self.app.test_client() as client:

            response = client.post(
                'http://localhost:5000/people/',
                headers = HEADERS,
                data  = {
                    'username': 'bob',
                    'name': 'Bob Billy',
                    'email': 'bbob@example.com',
                    'website': 'http://bbob.example.com',
                    'password': 'password1234',
                })

            response = client.put(
                'http://localhost:5000/people/bob',
                headers = HEADERS,
                data  = {
                    'username': 'bob',
                    'name': 'Jim Billy',
                    'email': 'jbob@example.com',
                    'website': 'http://jbob.example.com',
                })
        
            self.assertEqual(
                json.loads(response.data),
                {'email': 'jbob@example.com',
                 'id': 2,
                 'name': 'Jim Billy',
                 'username': 'bob',
                 'website': 'http://jbob.example.com',
                 'gravatar_email': None,
                 'gravatar_id': None,
                 'avatar_url': None,
                 })


            response = client.get(
                'http://localhost:5000/people/bob')

            self.assertEqual(
                json.loads(response.data),
                {
                    'id': 2,
                    'username': 'bob',
                    'name': 'Jim Billy',
                    'email': 'jbob@example.com',
                    'website': 'http://jbob.example.com',
                    'gravatar_email': None,
                    'gravatar_id': None,
                    'avatar_url': None,
                })

    @freeze_time("2012-01-14 12:00:01")
    def test_update_non_existing_person_by_id(self):
        with self.app.test_client() as client:

            response = client.put(
                'http://localhost:5000/people/2',
                headers = HEADERS,
                data  = {
                    'username': 'bob',
                    'name': 'Jim Billy',
                    'email': 'jbob@example.com',
                    'website': 'http://jbob.example.com',
                    'password': 'password1234',
                })
        
            self.assertEqual(
                json.loads(response.data),
                { 'exception': 'LookupError',
                  'message': 'person not found' })


    @freeze_time("2012-01-14 12:00:01")
    def test_update_non_existing_person_by_username(self):
        with self.app.test_client() as client:


            response = client.put(
                'http://localhost:5000/people/bob',
                headers = HEADERS,
                data  = {
                    'username': 'bob',
                    'name': 'Jim Billy',
                    'email': 'jbob@example.com',
                    'website': 'http://jbob.example.com',
                    'password': 'password1234',
                })
        
            self.assertEqual(
                json.loads(response.data),
                { 'exception': 'LookupError',
                  'message': 'person not found' })

