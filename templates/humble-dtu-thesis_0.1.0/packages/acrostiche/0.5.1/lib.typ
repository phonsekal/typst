#let acrostiche-state = state("acrostiche-state", (
  acronyms: (:),
  used: ()
))

#let init-acronyms(defs) = {
  acrostiche-state.update(state => {
    let acrs = state.acronyms
    if type(defs) == dictionary {
      for (k, v) in defs {
        acrs.insert(k, v)
      }
    } else if type(defs) == array {
      for item in defs {
        if type(item) == array and item.len() >= 2 {
          acrs.insert(item.at(0), item.at(1))
        }
      }
    }
    state.acronyms = acrs
    state
  })
}

#let display-def(acr, plural: false) = {
  context {
    let st = acrostiche-state.get()
    if acr in st.acronyms {
      let def = st.acronyms.at(acr)
      if type(def) == dictionary {
        if plural and "plural" in def {
          def.plural
        } else if "long" in def {
          def.long
        } else {
          str(def)
        }
      } else {
        str(def)
      }
    } else {
      text(fill: rgb("ff0000"), "[" + acr + "?]")
    }
  }
}

#let display-short(acr, plural: false) = {
  if plural {
    acr + "s"
  } else {
    acr
  }
}

#let mark-acr-used(acr) = {
  acrostiche-state.update(state => {
    if not acr in state.used {
      state.used.push(acr)
    }
    state
  })
}

#let acr(acr_name, plural: false) = {
  context {
    let st = acrostiche-state.get()
    if acr_name in st.used {
      display-short(acr_name, plural: plural)
    } else {
      let def_val = display-def(acr_name, plural: plural)
      let short_val = display-short(acr_name, plural: plural)
      mark-acr-used(acr_name)
      [#def_val (#short_val)]
    }
  }
}

#let acrpl(acronym) = { acr(acronym, plural: true) }

#let acrfull(acr_name) = {
  let def_val = display-def(acr_name, plural: false)
  let short_val = display-short(acr_name, plural: false)
  mark-acr-used(acr_name)
  [#def_val (#short_val)]
}

#let acrfullpl(acr_name) = {
  let def_val = display-def(acr_name, plural: true)
  let short_val = display-short(acr_name, plural: true)
  mark-acr-used(acr_name)
  [#def_val (#short_val)]
}

#let reset-acronym(acr_name) = {
  acrostiche-state.update(state => {
    let new-used = ()
    for item in state.used {
      if item != acr_name {
        new-used.push(item)
      }
    }
    state.used = new-used
    state
  })
}

#let reset-all-acronyms() = {
  acrostiche-state.update(state => {
    state.used = ()
    state
  })
}

// Alias fungsi
#let acrf(a) = acrfull(a)
#let acrfpl(a) = acrfullpl(a)
#let racr(a) = reset-acronym(a)
#let raacr() = reset-all-acronyms()
#let acresetall = reset-all-acronyms
#let ac = acr
#let acp(a) = acr(a, plural: true)
#let acl(a) = display-def(a, plural: false)
#let aclp(a) = display-def(a, plural: true)
#let acf(a) = acrf(a)
#let acfp(a) = acrfpl(a)
#let acs(a) = display-short(a, plural: false)
#let acsp(a) = display-short(a, plural: true)
#let acused(a) = mark-acr-used(a)

#let print-index(level: 1, numbering: none, outlined: false, sorted: "") = {
  context {
    let st = acrostiche-state.get()
    let keys = st.acronyms.keys()
    if sorted == "are" or sorted == "asc" {
      keys = keys.sorted()
    }
    for k in keys {
      let def_val = display-def(k)
      [ - *#k*: #def_val \ ]
    }
  }
}
