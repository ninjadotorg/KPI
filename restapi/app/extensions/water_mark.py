#!/usr/bin/python
# -*- coding: utf-8 -*-
from cStringIO import StringIO

from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, KeepInFrame
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import GOV_LEGAL
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.lib.units import inch
from datetime import datetime

import time
import pytz
import os.path as path
import app.constants as CONST


class WaterMark(object):
    def __init__(self, app=None):
        super(WaterMark, self).__init__()
        if app:
            self.app = app

    def init_app(self, app):
        self.app = app

    def _icolor(self, industries_type):
        icolor = 1
        if industries_type == 1 or \
                        industries_type == 3 or \
                        industries_type == 5:
            icolor = 2
        elif industries_type == 2 or \
                        industries_type == 4 or \
                        industries_type == CONST.Handshake['INDUSTRIES_UPLOAD_DOCUMENT']:
            icolor = 3

        return icolor

    '''
        Create payer signature
    '''

    def add_payer_signature(self, file_path, industries_type, tx):
        if tx is not None:
            PAGE_WIDTH, _ = GOV_LEGAL

            tx_signer_title = 'By:'
            tx_block_title = 'Block Number:'
            tx_time_title = 'Block Time:'
            tx_hash_title = 'TxHash:'
            tx_email_title = 'Name:' if tx.user.name is not None and len(tx.user.name) > 0 else 'Email:'

            to_tx_time = datetime.fromtimestamp(int(tx.block_time_stamp), tz=pytz.utc)
            to_tx_signer = tx.user.wallet.address
            to_tx_block = tx.block_number
            to_tx_time = to_tx_time.strftime('%a %b %d %Y %H:%M:%S GMT%z (%Z)')
            to_tx_hash = tx.hash
            to_tx_email = tx.user.name if tx.user.name is not None and len(tx.user.name) > 0 else tx.user.email

            base = path.basename(file_path)
            filename, file_extension = path.splitext(base)
            pdf_path = path.abspath(path.join(__file__, '../..')) + '/files/pdf/'

            millis = int(round(time.time()))
            water_pdf_name = 'watermark' + str(millis) + '.pdf'
            output_pdf_name = 'Email:' + filename + str(millis) + '_signed.pdf'

            icolor = self._icolor(industries_type)

            # Create the watermark from an image
            c = canvas.Canvas(pdf_path + '/' + water_pdf_name)

            # move the origin up and to the left
            c.translate(inch, inch)

            # change color

            if icolor == 3:
                c.setFillColorRGB(0, 0, 0)
            else:
                c.setFillColorRGB(255, 255, 255)

            # define a large font
            c.setFont("Helvetica", 14)

            # draw tx
            c.drawString(-10, 1.7 * inch, tx_signer_title)
            c.drawString(-10, 1.37 * inch, tx_block_title)
            c.drawString(-10, 1.04 * inch, tx_hash_title)
            c.drawString(-10, 0.38 * inch, tx_time_title)
            c.drawString(-10, 0.05 * inch, tx_email_title)

            c.drawString(1.4 * inch, 1.7 * inch, to_tx_signer)
            c.drawString(1.4 * inch, 1.37 * inch, to_tx_block)
            c.drawString(1.4 * inch, 1.04 * inch, to_tx_hash[:32])
            c.drawString(1.4 * inch, 0.71 * inch, to_tx_hash[32:])
            c.drawString(1.4 * inch, 0.38 * inch, to_tx_time)
            c.drawString(1.4 * inch, 0.05 * inch, to_tx_email)

            c.showPage()
            c.save()

            # Get the watermark file you just created
            watermark = PdfFileReader(open(pdf_path + "/" + water_pdf_name, "rb"))

            # Get our files ready
            output_file = PdfFileWriter()

            input_file = PdfFileReader(open(file_path, "rb"))
            # Number of pages in input document
            page_count = input_file.getNumPages()

            # Go through all the input file pages to add a watermark to them
            for page_number in range(page_count):
                input_page = input_file.getPage(page_number)
                # print input_page
                if page_number == page_count - 1:
                    # merge the watermark with the page
                    input_page.mergePage(watermark.getPage(0))
                # add page from input file to output document
                output_file.addPage(input_page)
            # finally, write "output" to document-output.pdf
            with open(pdf_path + output_pdf_name, "wb") as outputStream:
                output_file.write(outputStream)
                outputStream.close()
            return pdf_path + output_pdf_name
        return ''

    '''
        Create payee signature
    '''

    def add_payee_signature(self, file_path, industries_type, tx):
        if tx is not None:
            base = path.basename(file_path)
            filename, file_extension = path.splitext(base)
            pdf_path = path.abspath(path.join(__file__, '../..')) + '/files/pdf/'

            millis = int(round(time.time()))
            water_pdf_name = 'watermark' + str(millis) + '.pdf'
            output_pdf_name = 'Email:' + filename + str(millis) + '_signed.pdf'

            tx_signer_title = 'By:'
            tx_block_title = 'Block Number:'
            tx_time_title = 'Block Time:'
            tx_hash_title = 'TxHash:'
            tx_email_title = 'Name:' if tx.user.name is not None and len(tx.user.name) > 0 else 'Email:'

            from_tx_time = datetime.fromtimestamp(int(tx.block_time_stamp), tz=pytz.utc)
            from_tx_signer = tx.user.wallet.address
            from_tx_block = tx.block_number
            from_tx_time = from_tx_time.strftime('%a %b %d %Y %H:%M:%S GMT%z (%Z)')
            from_tx_hash = tx.hash
            from_tx_email = tx.user.name if tx.user.name is not None and len(tx.user.name) > 0 else tx.user.email

            # Create the watermark from an image
            c = canvas.Canvas(pdf_path + '/' + water_pdf_name, pagesize=GOV_LEGAL)
            c_width, c_height = GOV_LEGAL

            # move the origin up and to the left
            c.translate(inch, inch)

            icolor = self._icolor(industries_type)

            # change color
            if icolor == 3:
                c.setFillColorRGB(0, 0, 0)
            else:
                c.setFillColorRGB(255, 255, 255)

            # add line
            c.setFont("Courier-Bold", 20)
            c.drawString(-10, 4.5 * inch, '____')

            # draw tx
            c.setFont("Helvetica", 14)
            c.drawString(-10, 4.14 * inch, tx_signer_title)
            c.drawString(-10, 3.81 * inch, tx_block_title)
            c.drawString(-10, 3.48 * inch, tx_hash_title)
            c.drawString(-10, 2.82 * inch, tx_time_title)
            c.drawString(-10, 2.49 * inch, tx_email_title)

            c.drawString(1.4 * inch, 4.14 * inch, from_tx_signer)
            c.drawString(1.4 * inch, 3.81 * inch, from_tx_block)
            c.drawString(1.4 * inch, 3.48 * inch, from_tx_hash[:32])
            c.drawString(1.4 * inch, 3.15 * inch, from_tx_hash[32:])
            c.drawString(1.4 * inch, 2.82 * inch, from_tx_time)
            c.drawString(1.4 * inch, 2.49 * inch, from_tx_email)

            c.showPage()
            c.save()

            # create canvas for final stamp
            stamp_pdf_name = 'stamp' + str(millis) + '.pdf'
            c_stamp = canvas.Canvas(pdf_path + '/' + stamp_pdf_name)
            c_stamp.drawImage(self.app.config['FILE_FOLDER'] + '/final_stamp.png', c_width - 155, 3.0 * inch, width=120,
                              height=120, mask='auto', anchor='nw')
            c_stamp.showPage()
            c_stamp.save()

            # Get the watermark file you just created
            watermark = PdfFileReader(open(pdf_path + "/" + water_pdf_name, "rb"))
            stamp = PdfFileReader(open(pdf_path + "/" + stamp_pdf_name, "rb"))

            # Get our files ready
            output_file = PdfFileWriter()
            input_file = PdfFileReader(open(file_path, "rb"))
            page_count = input_file.getNumPages()

            # Go through all the input file pages to add a watermark to them
            for page_number in range(page_count):
                input_page = input_file.getPage(page_number)
                # print input_page
                if page_number == page_count - 1:
                    # merge the watermark with the page
                    input_page.mergePage(watermark.getPage(0))
                    input_page.mergePage(stamp.getPage(0))

                # add page from input file to output document
                output_file.addPage(input_page)

            # finally, write "output" to document-output.pdf
            with open(pdf_path + output_pdf_name, "wb") as outputStream:
                output_file.write(outputStream)
                outputStream.close()
            return pdf_path + output_pdf_name

        return ''

    '''
        Create content for empty handshake file
    '''

    def add_description(self, description, industries_type, file_path):
        base = path.basename(file_path)
        filename, file_extension = path.splitext(base)
        pdf_path = path.abspath(path.join(__file__, '../..')) + '/files/pdf/'

        millis = int(round(time.time()))
        water_pdf_name = 'watermark' + str(millis) + '.pdf'
        signature_pdf_name = 'signature' + str(millis) + '.pdf'
        output_pdf_name = 'Email:' + filename + str(millis) + '_signed.pdf'

        # create canvas for content
        c = canvas.Canvas(pdf_path + '/' + water_pdf_name, pagesize=GOV_LEGAL, bottomup=0)
        c_width, c_height = GOV_LEGAL

        # add background
        icolor = self._icolor(industries_type)
        c.drawImage(self.app.config['FILE_FOLDER'] + "/bg_{}.png".format(icolor), 0, 0, width=c_width, height=c_height,
                    mask='auto', anchor='nw')

        # move the origin up and to the left
        c.translate(inch, inch)

        # change color
        if icolor == 3:
            c.setFillColorRGB(0, 0, 0)
        else:
            c.setFillColorRGB(255, 255, 255)

        # add handshake title
        c.setFont("Helvetica", 23)
        c.drawString(-10, 0.5 * inch, 'The Handshake')

        # define a large font
        stylesheet = getSampleStyleSheet()
        style = stylesheet['Normal']
        style.fontName = 'Courier-Bold'
        style.fontSize = 34
        style.leading = style.fontSize * 1.2
        if icolor == 3:
            style.textColor = colors.black
        else:
            style.textColor = colors.white

        p = Paragraph(description, style)
        f = KeepInFrame(c_width + 20 - 2 * inch, c_height, [p], vAlign='TOP')
        width, height = f.wrapOn(c, c_width + 40 - 2 * inch, c_height)
        f.drawOn(c, -10, -height - 20 + (2.8 * inch))

        c.showPage()
        c.save()

        # Get the watermark file you just created
        watermark = PdfFileReader(open(pdf_path + "/" + water_pdf_name, "rb"))
        signature = None

        # create signature page if any
        if len(description) > 160:
            c_signature = canvas.Canvas(pdf_path + '/' + signature_pdf_name, pagesize=GOV_LEGAL, bottomup=0)

            # add background
            c_signature.drawImage(self.app.config['FILE_FOLDER'] + "/bg_{}.png".format(icolor), 0, 0, width=c_width,
                                  height=c_height, mask='auto', anchor='nw')

            c_signature.showPage()
            c_signature.save()

            signature = PdfFileReader(open(pdf_path + "/" + signature_pdf_name, "rb"))

        # Get our files ready
        output_file = PdfFileWriter()
        watermark_page = watermark.getPage(0)
        output_file.addPage(watermark_page)
        if signature is not None:
            output_file.addPage(signature.getPage(0))

        # finally, write "output" to document-output.pdf
        with open(pdf_path + output_pdf_name, "wb") as outputStream:
            output_file.write(outputStream)
            outputStream.close()
        return pdf_path + output_pdf_name

    '''
        Create empty page
    '''

    def add_empty_page(self, file_path):
        base = path.basename(file_path)
        filename, file_extension = path.splitext(base)
        pdf_path = path.abspath(path.join(__file__, '../..')) + '/files/pdf/'

        millis = int(round(time.time()))
        signature_pdf_name = 'signature' + str(millis) + '.pdf'
        output_pdf_name = 'Email:' + filename + str(millis) + '_signed.pdf'

        c = canvas.Canvas(pdf_path + '/' + signature_pdf_name, pagesize=GOV_LEGAL, bottomup=0)
        c.setFillColorRGB(255, 255, 255)
        c.showPage()
        c.save()
        signature = PdfFileReader(open(pdf_path + "/" + signature_pdf_name, "rb"))

        # Get our files ready
        output_file = PdfFileWriter()

        input_file = PdfFileReader(open(file_path, "rb"))
        # Number of pages in input document
        page_count = input_file.getNumPages()

        # Go through all the input file pages to add a watermark to them
        for page_number in range(page_count):
            input_page = input_file.getPage(page_number)
            output_file.addPage(input_page)

        output_file.addPage(signature.getPage(0))
        # finally, write "output" to document-output.pdf
        with open(pdf_path + output_pdf_name, "wb") as outputStream:
            output_file.write(outputStream)
            outputStream.close()
        return pdf_path + output_pdf_name
