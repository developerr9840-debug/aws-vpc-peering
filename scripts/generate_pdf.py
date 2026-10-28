import sys
import reportlab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

pdf_filename = 'Akhil_EWB_VPC_Peering.pdf'
doc = SimpleDocTemplate(
    pdf_filename,
    pagesize=letter,
    rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
)

styles = getSampleStyleSheet()
normal = styles['Normal']

# Custom Palette
PRIMARY = colors.HexColor('#0f172a')   # Deep Slate / Navy
SECONDARY = colors.HexColor('#0284c7') # Bright Blue
ACCENT = colors.HexColor('#0d9488')    # Teal
TEXT_DARK = colors.HexColor('#1e293b') # Dark Charcoal
BG_LIGHT = colors.HexColor('#f8fafc')  # Soft Grey

# Custom Paragraph Styles
title_style = ParagraphStyle('CoverTitle', parent=normal, fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=PRIMARY, alignment=1)
subtitle_style = ParagraphStyle('CoverSubtitle', parent=normal, fontName='Helvetica', fontSize=13, leading=16, textColor=SECONDARY, alignment=1)
meta_style = ParagraphStyle('CoverMeta', parent=normal, fontName='Helvetica', fontSize=9.5, leading=13, textColor=TEXT_DARK, alignment=1)

h1_style = ParagraphStyle('H1', parent=normal, fontName='Helvetica-Bold', fontSize=14, leading=17, textColor=PRIMARY, spaceBefore=10, spaceAfter=5)
body_style = ParagraphStyle('Body', parent=normal, fontName='Helvetica', fontSize=9, leading=13, textColor=TEXT_DARK, spaceBefore=3, spaceAfter=3)
table_text = ParagraphStyle('TableText', parent=normal, fontName='Helvetica', fontSize=8, leading=10, textColor=TEXT_DARK)
table_header = ParagraphStyle('TableHeader', parent=normal, fontName='Helvetica-Bold', fontSize=8.5, leading=10, textColor=colors.white)

story = []

# --- COVER HEADER ---
story.append(Spacer(1, 10))
story.append(Paragraph("EWB CLOUD LABS — VPC PEERING STUDENT PROJECT", subtitle_style))
story.append(Spacer(1, 6))
story.append(Paragraph("AWS Cross-VPC Peering &amp; Secure Communication", title_style))
story.append(Spacer(1, 10))
story.append(HRFlowable(width="100%", thickness=2, color=SECONDARY, spaceAfter=10))

# Meta Info Table
meta_data = [
    [Paragraph("<b>Student Name:</b> Akhil", meta_style), Paragraph("<b>Batch:</b> AWS Architect Associate", meta_style)],
    [Paragraph("<b>Target Region:</b> ap-southeast-2 (Sydney)", meta_style), Paragraph("<b>Completion Date:</b> 28 October 2026", meta_style)]
]
t_meta = Table(meta_data, colWidths=[270, 270])
t_meta.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
    ('PADDING', (0,0), (-1,-1), 6),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1'))
]))
story.append(t_meta)
story.append(Spacer(1, 10))

# --- SECTION 1: ARCHITECTURE OVERVIEW ---
story.append(Paragraph("1. Executive Architecture Overview", h1_style))
story.append(Paragraph("This project implements a secure cross-VPC networking infrastructure connecting two non-overlapping Virtual Private Clouds (<b>VPC A: 10.10.0.0/16</b> and <b>VPC B: 10.20.0.0/16</b>) via an AWS VPC Peering Connection (<code>ewb-a-b-peer</code>). Workloads <code>ewb-app-a</code> and <code>ewb-app-b</code> remain strictly private with zero public IP addresses.", body_style))

# Insert Architecture Diagram
story.append(Spacer(1, 4))
story.append(Image('docs/architecture-diagram.png', width=540, height=270))
story.append(Spacer(1, 8))

# --- SECTION 2: RESOURCE INVENTORY ---
story.append(Paragraph("2. Complete Resource Inventory", h1_style))
inv_data = [
    [Paragraph("Resource Name", table_header), Paragraph("Resource Type", table_header), Paragraph("CIDR / IP", table_header), Paragraph("Parent VPC / Subnet", table_header), Paragraph("Public IPv4", table_header)],
    [Paragraph("ewb-vpc-a", table_text), Paragraph("AWS::EC2::VPC", table_text), Paragraph("10.10.0.0/16", table_text), Paragraph("N/A", table_text), Paragraph("N/A", table_text)],
    [Paragraph("ewb-a-public", table_text), Paragraph("AWS::EC2::Subnet", table_text), Paragraph("10.10.1.0/24", table_text), Paragraph("ewb-vpc-a", table_text), Paragraph("Enabled", table_text)],
    [Paragraph("ewb-a-private", table_text), Paragraph("AWS::EC2::Subnet", table_text), Paragraph("10.10.2.0/24", table_text), Paragraph("ewb-vpc-a", table_text), Paragraph("Disabled", table_text)],
    [Paragraph("ewb-vpc-b", table_text), Paragraph("AWS::EC2::VPC", table_text), Paragraph("10.20.0.0/16", table_text), Paragraph("N/A", table_text), Paragraph("N/A", table_text)],
    [Paragraph("ewb-b-private", table_text), Paragraph("AWS::EC2::Subnet", table_text), Paragraph("10.20.1.0/24", table_text), Paragraph("ewb-vpc-b", table_text), Paragraph("Disabled", table_text)],
    [Paragraph("ewb-bastion", table_text), Paragraph("EC2 (t3.micro)", table_text), Paragraph("10.10.1.10", table_text), Paragraph("ewb-a-public", table_text), Paragraph("Auto-assign", table_text)],
    [Paragraph("ewb-app-a", table_text), Paragraph("EC2 (t3.micro)", table_text), Paragraph("10.10.2.10", table_text), Paragraph("ewb-a-private", table_text), Paragraph("None", table_text)],
    [Paragraph("ewb-app-b", table_text), Paragraph("EC2 (t3.micro)", table_text), Paragraph("10.20.1.10", table_text), Paragraph("ewb-b-private", table_text), Paragraph("None", table_text)]
]
t_inv = Table(inv_data, colWidths=[90, 110, 90, 150, 100])
t_inv.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), PRIMARY),
    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
    ('PADDING', (0,0), (-1,-1), 3)
]))
story.append(t_inv)
story.append(Spacer(1, 8))

# --- SECTION 3: ROUTE TABLES & SECURITY GROUPS ---
story.append(Paragraph("3. Ingress Security Rules Matrix", h1_style))

sg_data = [
    [Paragraph("Security Group", table_header), Paragraph("Ingress Protocol", table_header), Paragraph("Port / Type", table_header), Paragraph("Source CIDR / Host", table_header), Paragraph("Purpose / Rationale", table_header)],
    [Paragraph("ewb-sg-bastion", table_text), Paragraph("TCP", table_text), Paragraph("Port 22", table_text), Paragraph("&lt;Admin-IP&gt;/32", table_text), Paragraph("SSH access from student laptop", table_text)],
    [Paragraph("ewb-sg-app-a", table_text), Paragraph("TCP", table_text), Paragraph("Port 22", table_text), Paragraph("10.10.1.10/32", table_text), Paragraph("ProxyJump SSH from Bastion", table_text)],
    [Paragraph("ewb-sg-app-a", table_text), Paragraph("ICMP", table_text), Paragraph("Echo (8/0)", table_text), Paragraph("10.20.1.10/32", table_text), Paragraph("Cross-VPC ping from App-B", table_text)],
    [Paragraph("ewb-sg-app-b", table_text), Paragraph("TCP", table_text), Paragraph("Port 22", table_text), Paragraph("10.10.1.10/32", table_text), Paragraph("ProxyJump SSH from Bastion", table_text)],
    [Paragraph("ewb-sg-app-b", table_text), Paragraph("ICMP", table_text), Paragraph("Echo (8/0)", table_text), Paragraph("10.10.2.10/32", table_text), Paragraph("Cross-VPC ping from App-A", table_text)]
]
t_sg = Table(sg_data, colWidths=[100, 80, 80, 110, 170])
t_sg.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), SECONDARY),
    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
    ('PADDING', (0,0), (-1,-1), 3)
]))
story.append(t_sg)
story.append(Spacer(1, 8))

# --- SECTION 4: TEST RESULTS & CONTROLLED FAILURE ---
story.append(Paragraph("4. Offline Simulation Suite &amp; Live AWS Diagnostics", h1_style))

test_data = [
    [Paragraph("Test Scenario", table_header), Paragraph("Source Host &amp; Command", table_header), Paragraph("Expected Behavior", table_header), Paragraph("Classification &amp; Result", table_header)],
    [Paragraph("01 / Baseline", table_text), Paragraph("App-A: ping -c 4 10.20.1.10", table_text), Paragraph("100% Packet Loss (No Peering Route)", table_text), Paragraph("PASSED (Simulated)", table_text)],
    [Paragraph("02 / Forward Path", table_text), Paragraph("App-A: ping -c 4 10.20.1.10", table_text), Paragraph("4 replies received; 0% loss", table_text), Paragraph("PASSED (Simulated)", table_text)],
    [Paragraph("03 / Reverse Path", table_text), Paragraph("App-B: ping -c 4 10.10.2.10", table_text), Paragraph("4 replies received; 0% loss", table_text), Paragraph("PASSED (Simulated)", table_text)],
    [Paragraph("04 / SSH ProxyJump", table_text), Paragraph("Laptop: ssh ewb-app-b", table_text), Paragraph("Secure shell opened on App-B via Bastion", table_text), Paragraph("PASSED (Simulated)", table_text)],
    [Paragraph("05 / Isolation", table_text), Paragraph("Console: Check App-A &amp; App-B", table_text), Paragraph("No Public IPv4 assigned to either workload", table_text), Paragraph("PASSED (Simulated)", table_text)]
]
t_test = Table(test_data, colWidths=[90, 160, 200, 90])
t_test.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), ACCENT),
    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
    ('PADDING', (0,0), (-1,-1), 3)
]))
story.append(t_test)
story.append(Spacer(1, 6))

story.append(Paragraph("<b>Live AWS Observation &amp; Analysis:</b> A live ping from Bastion (<code>10.10.1.10</code>) to App-B (<code>10.20.1.10</code>) resulted in 100% packet loss. This is <b>expected and correct</b> because App-B's security group strictly allows ICMP Echo Requests from App-A (<code>10.10.2.10/32</code>), NOT from Bastion. End-to-end live testing requires running ping from inside App-A.", body_style))
story.append(Spacer(1, 8))

# --- SECTION 5: TECHNICAL VIVA QUESTIONS ---
story.append(Paragraph("5. Technical Viva &amp; Architectural Defense Answers", h1_style))
story.append(Paragraph("<b>Q1: Why is the return route required in ewb-rt-b-private?</b><br/>"
                       "<i>Answer:</i> IP routing is bidirectional. While the forward route sends packets to VPC B, replies from App-B destined for 10.10.2.10 require an explicit return route in VPC B's route table pointing 10.10.0.0/16 to the peering connection.", body_style))
story.append(Paragraph("<b>Q2: Why is the App-B SSH source IP address the Bastion private IP (10.10.1.10)?</b><br/>"
                       "<i>Answer:</i> ProxyJump establishes an SSH tunnel to the Bastion host, which then initiates a new TCP connection to App-B from its own private IP (10.10.1.10).", body_style))
story.append(Paragraph("<b>Q3: Why does Active peering not guarantee successful ping reachability?</b><br/>"
                       "<i>Answer:</i> Peering provides physical connectivity layer; reachability requires subnet route tables pointing to the peering ID and Security Groups allowing the specific ICMP traffic.", body_style))
story.append(Paragraph("<b>Q4: Can VPC B access the Internet using VPC A's Internet Gateway over peering?</b><br/>"
                       "<i>Answer:</i> No. VPC Peering is non-transitive and does not support edge-to-edge gateway transit.", body_style))

# --- SECTION 6: CLEANUP & SAFETY ---
story.append(Spacer(1, 8))
story.append(Paragraph("6. AWS Safety, Cost Control &amp; Cleanup", h1_style))
story.append(Paragraph("All resources are managed via CloudFormation (<code>infrastructure/vpc-peering.yaml</code>) in region <code>ap-southeast-2</code> using cost-effective <code>t3.micro</code> instances without billable NAT Gateways. Total estimated cost is under $0.05/hr. Full teardown can be executed in one command: <code>aws cloudformation delete-stack --stack-name ewb-vpc-peering-lab</code>.", body_style))

doc.build(story)
print('PDF generated successfully:', pdf_filename)
