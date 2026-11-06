import zipfile
import os

def create_presentation(output_path="Project_Review_Presentation.pptx"):
    slides_data = [
        {
            "title": "Multiplayer In-Game Cheat Detection System",
            "subtitle": "Real-Time Telemetry Analysis, Kinematic Modeling & 3-Tier Classification",
            "bullets": [
                "Project Review / Viva Defense Presentation",
                "Domain: Cyber-Physical Systems, Machine Learning & Game Security",
                "Core Innovation: Server-Authoritative Kinematic Behavioral Analytics",
                "Key Metric: 99.86% Detection Accuracy with 1.0000 ROC-AUC Score",
                "Complete End-to-End Pipeline: From Player Auth to Moderator Audit"
            ]
        },
        {
            "title": "Problem Statement & Industry Motivation",
            "subtitle": "The Evolving Threat of Algorithmic Cheating in Online Esports",
            "bullets": [
                "The Epidemic: Aimbots, Triggerbots, and Speedhacks undermine fair play and retention.",
                "Signature Anti-Cheat Failures: Polymorphic exploits bypass client-side binary scanning.",
                "Kernel-Level Dilemma: Drivers like Vanguard/BattlEye pose security and privacy concerns.",
                "Our Solution: Server-side behavioral & kinematic telemetry analysis with zero client hooks.",
                "Objective: Real-time 3-tier classification (Legit / Suspicious / Cheat) with human oversight."
            ]
        },
        {
            "title": "Proposed 10-Stage Architecture Pipeline",
            "subtitle": "End-to-End System Flow from Ingestion to Enforcement",
            "bullets": [
                "Stage A & B: Player Auth (JWT/BCrypt) and Dynamic Game Room Orchestration.",
                "Stage C: Automated 5-Player Minimum Threshold Guard with Bot Fillers.",
                "Stage D & E: Synchronous Game Simulation and 14-Metric Telemetry Streaming.",
                "Stage F & G: Trained Random Forest Inference & Continuous Probability Scoring.",
                "Stage H: 3-Tier Classification (Legitimate, Suspicious, Cheating).",
                "Stage I & J: Live Chart.js Analytical Dashboard & Human-in-the-Loop Moderator Review."
            ]
        },
        {
            "title": "Matchmaking & Room Management (Stages A - D)",
            "subtitle": "Lobby Architecture and Player Synchronization",
            "bullets": [
                "User Lifecycle: Secure registration, profile management, and session authentication.",
                "Room Configurator: Custom room modes (Deathmatch, Tactical), capacity (5-16), access codes.",
                "Threshold Validation: Hard requirement of 5 active players before match launch.",
                "Smart AI Bot Fillers: Auto-populates lobbies to test diverse player skill distributions.",
                "State Synchronization: Instant room state transitions from 'Waiting' to 'In-Progress'."
            ]
        },
        {
            "title": "Kinematic Feature Engineering (Stage E)",
            "subtitle": "14 Behavioral Telemetry Metrics Captured at Server Level",
            "bullets": [
                "Aim Dynamics: Headshot percentage, angular velocity, and aim jitter degrees/sec.",
                "Spatial & Movement: Spatial dispersion, movement acceleration, velocity anomalies.",
                "Reflex Latency: Reaction time distribution (ms) vs. human physiological limit (~120ms).",
                "Weapon Mastery: Burst fire consistency, accuracy drift under recoil pressure.",
                "Network Quality: Real-time ping variance and packet anomaly isolation."
            ]
        },
        {
            "title": "Machine Learning Pipeline (Stages F & G)",
            "subtitle": "Model Architecture, Training & Performance",
            "bullets": [
                "Algorithm Selection: Random Forest Classifier (100 Trees, Gini Impurity Criterion).",
                "Why Random Forest: Robust against non-linear kinematic interactions, avoids overfitting.",
                "Preprocessing: Robust Standard Scaling for variance normalization across play styles.",
                "Model Performance: 99.86% Test Accuracy, 1.0000 Area Under ROC Curve.",
                "Inference Latency: Sub-10ms evaluation per player event vector."
            ]
        },
        {
            "title": "3-Tier Classification Matrix (Stage H)",
            "subtitle": "Eliminating Binary False Positives via Multi-Tier Confidence",
            "bullets": [
                "The Binary Trap: Hard Cheat/No-Cheat models produce disastrous false bans.",
                "Legitimate Tier (Prob < 0.35): Normal human motor variability, natural jitter, human latency.",
                "Suspicious Tier (0.35 <= Prob < 0.75): Smurfs, erratic spikes, kinematic outliers flagged.",
                "Cheating Tier (Prob >= 0.75): Automated aim locks, zero-jitter snaps, unnatural reactions.",
                "Operational Benefit: Zero automatic false bans; suspicious players routed to queue."
            ]
        },
        {
            "title": "Visualization Analytics Dashboard (Stage I)",
            "subtitle": "High-Density Visual Telemetry for Live Match Oversight",
            "bullets": [
                "Executive KPIs: Live match count, total players screened, threat rate percentages.",
                "Donut Distribution: Visual breakdown of Legitimate vs. Suspicious vs. Cheating pool.",
                "Kinematic Scatter Plot: Accuracy (%) vs. Reaction Time (ms) clustering analysis.",
                "Feature Comparison: Interactive bar charts showing individual player anomalies.",
                "Interactive Pipeline Tracker: Visual breadcrumb showing progress from Stage A to J."
            ]
        },
        {
            "title": "Human-in-the-Loop Moderator Review (Stage J)",
            "subtitle": "Ethical AI Governance & Actionable Enforcement Desk",
            "bullets": [
                "Audit Workflow: Suspicious & Cheating players automatically populate moderator triage.",
                "Tri-State Filtering: Real-time filtering by status: 'All', 'Pending', 'Reviewed', 'Action Taken'.",
                "Telemetry Inspector: Deep dive into flagged player's angular velocities and kill feeds.",
                "Disciplinary Actions: Instant 1-click Ban, Flag for Watchlist, or Clear Player status.",
                "Audit Logging: Tamper-evident record of all moderation decisions with timestamps."
            ]
        },
        {
            "title": "Results, Conclusions & Future Roadmap",
            "subtitle": "System Validation, Academic Takeaways and Next Horizons",
            "bullets": [
                "System Validation: 8/8 comprehensive unit and integration test suites passing.",
                "Zero Client Dependency: High cheat detection accuracy without intrusive kernel rootkits.",
                "Extensibility: REST API architecture allows easy integration with Unreal / Unity backends.",
                "Future Scope - Phase 1: Temporal sequence modeling using Bi-LSTM / Transformer models.",
                "Future Scope - Phase 2: Graph Neural Networks (GNN) for detecting organized cheat rings."
            ]
        }
    ]

    # Namespaces
    a_ns = "http://schemas.openxmlformats.org/drawingml/2006/main"
    r_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    p_ns = "http://schemas.openxmlformats.org/presentationml/2006/main"

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as z:
        # [Content_Types].xml
        content_types = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
            '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
            '  <Default Extension="xml" ContentType="application/xml"/>',
            '  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
            '  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
            '  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
            '  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
        ]
        for i in range(1, len(slides_data) + 1):
            content_types.append(f'  <Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>')
        content_types.append('</Types>')
        z.writestr("[Content_Types].xml", "\n".join(content_types))

        # _rels/.rels
        rels = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
            '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>',
            '</Relationships>'
        ]
        z.writestr("_rels/.rels", "\n".join(rels))

        # ppt/_rels/presentation.xml.rels
        pres_rels = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
            '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
        ]
        for i in range(1, len(slides_data) + 1):
            pres_rels.append(f'  <Relationship Id="rId{i+1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>')
        pres_rels.append('</Relationships>')
        z.writestr("ppt/_rels/presentation.xml.rels", "\n".join(pres_rels))

        # ppt/presentation.xml
        pres = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            f'<p:presentation xmlns:a="{a_ns}" xmlns:r="{r_ns}" xmlns:p="{p_ns}">',
            '  <p:sldMasterIdLst>',
            '    <p:sldMasterId id="2147483648" r:id="rId1"/>',
            '  </p:sldMasterIdLst>',
            '  <p:sldIdLst>'
        ]
        for i in range(1, len(slides_data) + 1):
            pres.append(f'    <p:sldId id="{255+i}" r:id="rId{i+1}"/>')
        pres.extend([
            '  </p:sldIdLst>',
            '  <p:sldSz cx="12192000" cy="6858000"/>', # 16:9 widescreen
            '  <p:notesSz cx="6858000" cy="12192000"/>',
            '</p:presentation>'
        ])
        z.writestr("ppt/presentation.xml", "\n".join(pres))

        # ppt/theme/theme1.xml (Dark tech theme palette: Navy #0F172A, Cyan #06B6D4, Accent #3B82F6)
        theme = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            f'<a:theme xmlns:a="{a_ns}" name="TechDark">',
            '  <a:themeElements>',
            '    <a:clrScheme name="Cyber">',
            '      <a:dk1><a:srgbClr val="0F172A"/></a:dk1>',
            '      <a:lt1><a:srgbClr val="F8FAFC"/></a:lt1>',
            '      <a:dk2><a:srgbClr val="1E293B"/></a:dk2>',
            '      <a:lt2><a:srgbClr val="E2E8F0"/></a:lt2>',
            '      <a:accent1><a:srgbClr val="06B6D4"/></a:accent1>',
            '      <a:accent2><a:srgbClr val="3B82F6"/></a:accent2>',
            '      <a:accent3><a:srgbClr val="10B981"/></a:accent3>',
            '      <a:accent4><a:srgbClr val="F59E0B"/></a:accent4>',
            '      <a:accent5><a:srgbClr val="EF4444"/></a:accent5>',
            '      <a:accent6><a:srgbClr val="8B5CF6"/></a:accent6>',
            '      <a:hlink><a:srgbClr val="38BDF8"/></a:hlink>',
            '      <a:folHlink><a:srgbClr val="818CF8"/></a:folHlink>',
            '    </a:clrScheme>',
            '    <a:fontScheme name="Modern">',
            '      <a:majorFont><a:latin typeface="Segoe UI Semibold"/></a:majorFont>',
            '      <a:minorFont><a:latin typeface="Segoe UI"/></a:minorFont>',
            '    </a:fontScheme>',
            '    <a:fmtScheme name="Office">',
            '      <a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>',
            '      <a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="25400"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="38100"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>',
            '      <a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>',
            '      <a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst>',
            '    </a:fmtScheme>',
            '  </a:themeElements>',
            '</a:theme>'
        ]
        z.writestr("ppt/theme/theme1.xml", "\n".join(theme))

        # ppt/slideMasters/slideMaster1.xml
        sm = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            f'<p:sldMaster xmlns:a="{a_ns}" xmlns:r="{r_ns}" xmlns:p="{p_ns}">',
            '  <p:cSld>',
            '    <p:spTree>',
            '      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:grpSpPr/></p:nvGrpSpPr>',
            '      <p:grpSpPr/>',
            '    </p:spTree>',
            '  </p:cSld>',
            '  <p:clrMap bg1="dk1" tx1="lt1" bg2="dk2" tx2="lt2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>',
            '  <p:sldLayoutIdLst>',
            '    <p:sldLayoutId id="2147483649" r:id="rId1"/>',
            '  </p:sldLayoutIdLst>',
            '</p:sldMaster>'
        ]
        z.writestr("ppt/slideMasters/slideMaster1.xml", "\n".join(sm))

        sm_rels = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
            '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>',
            '  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>',
            '</Relationships>'
        ]
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", "\n".join(sm_rels))

        # ppt/slideLayouts/slideLayout1.xml
        sl = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            f'<p:sldLayout xmlns:a="{a_ns}" xmlns:r="{r_ns}" xmlns:p="{p_ns}" type="blank">',
            '  <p:cSld>',
            '    <p:spTree>',
            '      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:grpSpPr/></p:nvGrpSpPr>',
            '      <p:grpSpPr/>',
            '    </p:spTree>',
            '  </p:cSld>',
            '</p:sldLayout>'
        ]
        z.writestr("ppt/slideLayouts/slideLayout1.xml", "\n".join(sl))

        sl_rels = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
            '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>',
            '</Relationships>'
        ]
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", "\n".join(sl_rels))

        # Generate each slide
        for idx, sdata in enumerate(slides_data, start=1):
            slide_xml = [
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                f'<p:sld xmlns:a="{a_ns}" xmlns:r="{r_ns}" xmlns:p="{p_ns}">',
                '  <p:cSld>',
                '    <p:bg>',
                '      <p:bgPr>',
                '        <a:solidFill><a:srgbClr val="0F172A"/></a:solidFill>', # Dark navy background
                '      </p:bgPr>',
                '    </p:bg>',
                '    <p:spTree>',
                '      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:grpSpPr/></p:nvGrpSpPr>',
                '      <p:grpSpPr/>',
                
                # Header Banner / Top Line
                '      <p:sp>',
                '        <p:nvSpPr><p:cNvPr id="2" name="HeaderLine"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>',
                '        <p:spPr>',
                '          <a:xfrm><a:off x="600000" y="450000"/><a:ext cx="10992000" cy="40000"/></a:xfrm>',
                '          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>',
                '          <a:solidFill><a:srgbClr val="06B6D4"/></a:solidFill>',
                '        </p:spPr>',
                '      </p:sp>',

                # Slide Number Badge
                '      <p:sp>',
                '        <p:nvSpPr><p:cNvPr id="3" name="Badge"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>',
                '        <p:spPr>',
                '          <a:xfrm><a:off x="10600000" y="550000"/><a:ext cx="1000000" cy="350000"/></a:xfrm>',
                '          <a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 20000"/></a:avLst></a:prstGeom>',
                '          <a:solidFill><a:srgbClr val="1E293B"/></a:solidFill>',
                '          <a:ln w="12700"><a:solidFill><a:srgbClr val="334155"/></a:solidFill></a:ln>',
                '        </p:spPr>',
                '        <p:txBody>',
                '          <a:bodyPr anchor="ctr"/>',
                '          <a:p><a:pPr algn="ctr"/>',
                f'            <a:r><a:rPr sz="1200" b="1"><a:solidFill><a:srgbClr val="38BDF8"/></a:solidFill></a:rPr><a:t>SLIDE {idx:02d}/10</a:t></a:r>',
                '          </a:p>',
                '        </p:txBody>',
                '      </p:sp>',

                # Title Text Box
                '      <p:sp>',
                '        <p:nvSpPr><p:cNvPr id="4" name="TitleBox"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>',
                '        <p:spPr>',
                '          <a:xfrm><a:off x="600000" y="550000"/><a:ext cx="9800000" cy="1100000"/></a:xfrm>',
                '          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>',
                '          <a:noFill/>',
                '        </p:spPr>',
                '        <p:txBody>',
                '          <a:bodyPr anchor="t"/>',
                '          <a:p>',
                f'            <a:r><a:rPr sz="2600" b="1"><a:solidFill><a:srgbClr val="F8FAFC"/></a:solidFill></a:rPr><a:t>{sdata["title"]}</a:t></a:r>',
                '          </a:p>',
                '          <a:p>',
                f'            <a:r><a:rPr sz="1400" i="1"><a:solidFill><a:srgbClr val="94A3B8"/></a:solidFill></a:rPr><a:t>{sdata["subtitle"]}</a:t></a:r>',
                '          </a:p>',
                '        </p:txBody>',
                '      </p:sp>',

                # Content Card Background
                '      <p:sp>',
                '        <p:nvSpPr><p:cNvPr id="5" name="ContentCard"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>',
                '        <p:spPr>',
                '          <a:xfrm><a:off x="600000" y="1800000"/><a:ext cx="10992000" cy="4500000"/></a:xfrm>',
                '          <a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 15000"/></a:avLst></a:prstGeom>',
                '          <a:solidFill><a:srgbClr val="1E293B"/></a:solidFill>',
                '          <a:ln w="19050"><a:solidFill><a:srgbClr val="334155"/></a:solidFill></a:ln>',
                '        </p:spPr>',
                '        <p:txBody>',
                '          <a:bodyPr anchor="t" lIns="300000" tIns="300000" rIns="300000" bIns="300000"/>'
            ]

            # Bullets inside the card
            for b in sdata["bullets"]:
                parts = b.split(":", 1)
                slide_xml.append('          <a:p>')
                slide_xml.append('            <a:pPr marL="280000" indent="-280000">')
                slide_xml.append('              <a:buClr><a:srgbClr val="06B6D4"/></a:buClr>')
                slide_xml.append('              <a:buChar char="▪"/>')
                slide_xml.append('            </a:pPr>')
                if len(parts) == 2:
                    slide_xml.append(f'            <a:r><a:rPr sz="1600" b="1"><a:solidFill><a:srgbClr val="38BDF8"/></a:solidFill></a:rPr><a:t>{parts[0]}: </a:t></a:r>')
                    slide_xml.append(f'            <a:r><a:rPr sz="1600"><a:solidFill><a:srgbClr val="E2E8F0"/></a:solidFill></a:rPr><a:t>{parts[1]}</a:t></a:r>')
                else:
                    slide_xml.append(f'            <a:r><a:rPr sz="1600"><a:solidFill><a:srgbClr val="E2E8F0"/></a:solidFill></a:rPr><a:t>{b}</a:t></a:r>')
                slide_xml.append('          </a:p>')
                # Add spacing between bullets
                slide_xml.append('          <a:p><a:pPr><a:spcBef><a:spcPts val="1200"/></a:spcBef></a:pPr></a:p>')

            slide_xml.extend([
                '        </p:txBody>',
                '      </p:sp>',

                # Footer
                '      <p:sp>',
                '        <p:nvSpPr><p:cNvPr id="6" name="Footer"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>',
                '        <p:spPr>',
                '          <a:xfrm><a:off x="600000" y="6400000"/><a:ext cx="10992000" cy="300000"/></a:xfrm>',
                '          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>',
                '          <a:noFill/>',
                '        </p:spPr>',
                '        <p:txBody>',
                '          <a:bodyPr anchor="b"/>',
                '          <a:p>',
                '            <a:r><a:rPr sz="1000"><a:solidFill><a:srgbClr val="64748B"/></a:solidFill></a:rPr><a:t>Multiplayer In-Game Cheat Detection System (Aegis Anti-Cheat) | Project Review</a:t></a:r>',
                '          </a:p>',
                '        </p:txBody>',
                '      </p:sp>',

                '    </p:spTree>',
                '  </p:cSld>',
                '</p:sld>'
            ])
            z.writestr(f"ppt/slides/slide{idx}.xml", "\n".join(slide_xml))

            # Slide rels
            s_rels = [
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
                '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>',
                '</Relationships>'
            ]
            z.writestr(f"ppt/slides/_rels/slide{idx}.xml.rels", "\n".join(s_rels))

    print(f"[OK] Generated {output_path} successfully ({os.path.getsize(output_path)} bytes).")

if __name__ == "__main__":
    create_presentation()
